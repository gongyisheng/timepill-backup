# timepill-backup
胶囊日记备份程序，用于日记文本备份   
**使用问题**请提[issue](https://github.com/gongyisheng/timepill-backup/issues/new)或邮件联系yisheng_gong@onmail.com
### 可执行程序下载 
windows: [文件下载地址](https://github.com/gongyisheng/timepill-backup/releases/download/0.1.2/timepill-backup.exe)  
mac: [文件下载地址](https://github.com/gongyisheng/timepill-backup/releases/download/0.1.2/timepill-backup)  
### 二次开发:   
1. [下载python](https://www.python.org/)
2. [下载git](https://git-scm.com/downloads)
3. 打开一个命令行窗口（terminal）
4. 下载代码   
   `git clone https://github.com/gongyisheng/timepill-backup.git`
5. 进入project文件夹  
   `cd timepill-backup`
6. 安装依赖  
   `pip install -r requirement.txt`
7. 启动 **main.py** 程序  
   `python main.py`

#### 感谢原始代码作者[Libra](http://www.timepill.net/people/100699220), 项目后期由[小动物](http://timepill.net/people/100174502)维护

### Known Issue
- 程序运行会比较慢: 这是为了防止在短时间内发送大量请求至胶囊服务器，对其他用户的正常访问造成影响，实测完整备份10000条日记大概耗时10-15分钟，也取决于您的网络。
- 暂不支持评论备份: 这个功能可能导致服务器压力过大，请在[issue](https://github.com/gongyisheng/timepill-backup/issues/1)里投票让我知道需不需要实现该功能，图片备份也同理。