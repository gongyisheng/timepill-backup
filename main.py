import math
import xlwt
import requests
import json
from requests.auth import  HTTPBasicAuth

user_url="http://open.timepill.net:80/api/users/my"
notebook_url="http://open.timepill.net:80/api/notebooks/"
notebook_list_url="http://open.timepill.net:80/api/notebooks/my"
diary_url="http://open.timepill.net:80/api/diaries/"

headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/V11.0.5.0.PCACNXM)",
            "Host": "open.timepill.net:80",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
}

# get user id
def get_user_id(email, pwd, headers,url):
    res = requests.get(url=url, auth=HTTPBasicAuth(email, pwd), headers=headers)
    content = res.text
    decodejson = json.loads(content)  #将已编码的 JSON 字符串解码为 Python 对象，就是python解码json对象
    id = decodejson['id']
    return id

# get user notebook list
def get_user_notebooks(url):
    diaries_basic_infos= []
    diaries_basic_info=[]
    key=0
    res = requests.get(url=url, auth=HTTPBasicAuth(email, pwd), headers=headers)
    content = res.text
    decodejson = json.loads(content)  # 将已编码的 JSON 字符串解码为 Python 对象，就是python解码json对象
    for diaries_info in decodejson:
        diaries_id=diaries_info['id']
        diaries_subject=diaries_info['subject']
        diaries_create_time=diaries_info['created']
        diaries_basic_info.append(diaries_id)
        diaries_basic_info.append(diaries_subject)
        diaries_basic_info.append(diaries_create_time)
        diaries_basic_infos.insert(key,diaries_basic_info)
        diaries_basic_info=[]
        key=key+1
    return diaries_basic_infos

# get user diary
def get_user_diaries(diaries_basic_infos,url):
    workbook = xlwt.Workbook(encoding='utf-8')  # 新建工作簿
    sheet1 = workbook.add_sheet("日记备份")  # 新建sheet
    sheet1.write(0, 0, "日记本")  # 第1行第1列数据
    sheet1.write(0, 1, "内容")  # 第1行第2列数据
    sheet1.write(0, 2, "创建时间")  # 第1行第3列数据
    sheet1.write(0, 3, "图片链接")  # 第1行第4列数据
    sheet1.write(0, 4, "日记id")  #第1行第5列数据
    n = 1
    diaries_ids=[]
    ids=[]
    for diaries_basic_info in diaries_basic_infos:
        diaries_id=diaries_basic_info[0]
        diaries_ids.append(diaries_id)

    for diaries_id in diaries_ids:
        res = requests.get(url=url+str(diaries_id)+'/diaries', auth=HTTPBasicAuth(email, pwd), headers=headers, params={"page":1})
        content = res.text
        decodejson = json.loads(content)  # 将已编码的 JSON 字符串解码为 Python 对象，就是python解码json对象
        count = decodejson['count']
        total_pages = math.ceil(count / 20)
        page=1
        while page <= total_pages:
            res = requests.get(url=url + str(diaries_id) + '/diaries', auth=HTTPBasicAuth(email, pwd), headers=headers,
                               params={"page": page})
            content = res.text
            decodejson = json.loads(content)  # 将已编码的 JSON 字符串解码为 Python 对象，就是python解码json对象
            items = decodejson['items']

            for item in items:
                id = item['id']
                subject = item['notebook_subject']
                content = item['content']
                created_time = item['created']
                img = item['photoUrl']
                ids.append(id)
                sheet1.write(n, 0, subject)  # 第n行第1列数据
                sheet1.write(n, 1, content)  # 第n行第2列数据
                sheet1.write(n, 2, created_time)  # 第n行第3列数据
                sheet1.write(n, 3, img)  # 第n行第4列数据
                sheet1.write(n, 4, id)  # 第n行第4列数据
                n = n + 1
            print(decodejson)
            page = page+1
        workbook.save("日记.xls")  # 保存
    return ids

#账号密码
id = None
login_flag = False
while not login_flag:
    try:
        email = input("输入账号")
        pwd = input("输入密码")
        id = get_user_id(email, pwd, headers, user_url)
        login_flag = True
    except Exception:
        print("账号密码输入错误")

diaries_basic_infos = get_user_notebooks(notebook_list_url)
print(diaries_basic_infos)
ids = get_user_diaries(diaries_basic_infos, notebook_url)
input("完成! 按任意键退出")