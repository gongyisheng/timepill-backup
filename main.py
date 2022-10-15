import json
import os
import time

import pwinput
import requests
from requests.auth import  HTTPBasicAuth
from tqdm import tqdm
import xlwt

VERSION = "0.1.2"
# use https instead of http to avoid security concerns
# 使用https保证安全传输
user_url="https://open.timepill.net/api/users/my"
notebook_url="https://open.timepill.net/api/notebooks/"
notebook_list_url="https://open.timepill.net/api/notebooks/my"
diary_url="https://open.timepill.net/api/diaries/"

# 工作目录路径
work_dir = os.getcwd()

request_header = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/V11.0.5.0.PCACNXM)",
            "Host": "open.timepill.net:80",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Source": "TimepillBackup" # 标注source=backup，方便站长管理备份流量
}
excel_output_header = ["日记本", "内容", "创建时间", "图片链接", "日记id"]

notebook_extract_key = ['id', 'subject', 'created']
diary_extract_key = ['notebook_subject', 'content', 'created', 'photoUrl', 'id']

# util function to extract key from dict
# 从哈希表中按指定顺序提取key, 输出制定顺序value
def extract_key(dict, key_list):
    value_list = []
    for key in key_list:
        if key not in dict:
            print(f"WARNING: Key [{key}] is not in the response dict: {dict}")
        value_list.append(dict.get(key,""))
    return value_list

# generalized call api function 
# 通用的api调用方法，调用错误会将失败请求保存至fallback(如有)
def call_api(email, pwd, url, fallback=None, **kwargs):
    try:
        res = requests.get(url=url, auth=HTTPBasicAuth(email, pwd), headers=request_header, timeout=5, **kwargs) # max timeout = 5
        content = res.text
        content_decoded = json.loads(content)
        time.sleep(0.5) # sleep for 0.5s to avoid sending too many request to server in a short time
        return content_decoded
    except Exception as e:
        if fallback is not None:
            fallback.append({"url": url, **kwargs})
        print("Api调用错误, 原因: "+str(e))
        return None

# get user id 获取用户id
def get_user_id(email, pwd, url):
    _msg = call_api(email, pwd, url)
    id = _msg['id']
    return id

# get user notebook list 获取日记列表
def get_user_notebooks(email, pwd, url):
    notebook_list = []
    _msg = call_api(email, pwd, url)
    while _msg is None:
        flag = input("获取日记本信息失败,是否重试 y/n ")
        if flag != 'y':
            return []
        else:
            _msg = call_api(email, pwd, url)

    for notebook in _msg:
        notebook_item = extract_key(notebook, notebook_extract_key)
        notebook_list.append(notebook_item)
        
    return notebook_list

# total diary number of a notebook
diary_count = -1

# get user diary, it returns an iterator of diary items in a page 
# 获取用户日记, 返回一个遍历一页日记的迭代器
def get_user_diary_iter(email, pwd, url, page, fallback):
    global diary_count
    _msg = call_api(email, pwd, url, fallback, params={"page": page})
    if _msg is not None:
        diary_count = _msg["count"]
        diaries = _msg['items']
        for diary in diaries:
            diary_item = extract_key(diary, diary_extract_key)
            yield diary_item
    else:
        return []

# save diaries in a notebook until the end. If error, save the progress to fallback
# 保存日记本中的日记直到最后，如果保存失败，则在fallback列表中记录进度
def save_notebook_diary(email, pwd, workbook, notebook_url, fallback_list, start_page=1):
    global diary_count
    page = start_page
    is_end = False
    t = None
    rest_count = 0
    while not is_end:
        is_end = True
        for diary_item in get_user_diary_iter(email, pwd, notebook_url, page, fallback_list):
            workbook.save_diary(diary_item)
            is_end = False
        if is_end:
            break
        if t is None:
            t = tqdm(total=diary_count, desc=notebook_subject)
            rest_count = diary_count
        t.update(n=min(20, rest_count))
        rest_count -= 20
        page += 1
        
# current notebook subject
notebook_subject = None

# back up function 尝试保存每一本日记并备份至excel, 如果失败，记录失败时的进度
def backup(email, pwd, workbook, notebook_list, url):
    global notebook_subject
    fallback_list = [] # fallback list is designed to save failed requests temporarily

    for item in notebook_list:
        notebook_id = item[0]
        notebook_subject = item[1]
        notebook_url = url + str(notebook_id) + '/diaries'
        save_notebook_diary(email, pwd, workbook, notebook_url, fallback_list)

    workbook.save_workbook()
    return fallback_list

# class for excel output 备份输出文件的抽象类
class ExcelOutput(object):
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.workbook = xlwt.Workbook(encoding='utf-8') # 新建excel文件
        self.diary_sheet = self.workbook.add_sheet("日记备份")  # 新建sheet
        self.max_row = 0
    
    def set_header(self, header):
        for i in range(len(header)):
            self.diary_sheet.write(0, i, header[i])
        self.max_row = max(self.max_row, 1)

    # write diary item to diary sheet
    # 写入单条日记
    def save_diary(self, item):
        for i in range(len(item)):
            self.diary_sheet.write(self.max_row, i, item[i])
        self.max_row += 1
    
    # save workbook to disk
    # 保存整个excel文件到磁盘
    def save_workbook(self):
        self.workbook.save(self.output_dir+"/日记.xls")

# Welcome
print(f"<timepill-backup> 胶囊日记备份程序 v{VERSION}")
print(f"开发者: Libra, 小动物 | 联系方式见项目readme文档")
print(f"------------------------------------------—---")

# login 登录
id = None
email = None
pwd = None
login_flag = False
while not login_flag:
    try:
        email = input("输入邮箱")
        pwd = pwinput.pwinput(prompt="输入密码", mask='*')
        id = get_user_id(email, pwd, user_url)
        login_flag = True
    except Exception:
        print("账号密码输入错误, 请重试")

notebook_list = get_user_notebooks(email, pwd, notebook_list_url)
print(f"您有{len(notebook_list)}本日记本准备备份")
output = ExcelOutput(work_dir)
output.set_header(excel_output_header)
fallback_list = backup(email, pwd, output, notebook_list, notebook_url)

# if fallbacks
while len(fallback_list) != 0:
    flag = input(f"有{len(fallback_list)}本日记保存(或部分保存)失败,是否重试 y/n ")
    if flag.lower() != 'y':
        break
    _fallback_list = []
    for fallback_item in fallback_list:
        save_notebook_diary(email, pwd, output,fallback_item["url"], _fallback_list, fallback_item["params"]["page"])
    output.save_workbook()
    fallback_list = _fallback_list

input("完成! 按任意键退出")