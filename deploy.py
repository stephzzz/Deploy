"""
@author: Stephen
@file: deploy.py
@time: 2018/5/30 9:08
@python version: 3.5+
require: paramiko, svn
    pip install paramiko,svn

"""
import os
import paramiko
import re
import sys
import time
from svn import remote, local


class Deploy(object):
    def __init__(self, host, username, pwd):
        self.host = host
        self.username = username
        self.pwd = pwd
        self.port = 22

    def connect(self):
        transport = paramiko.Transport(self.host, self.port)
        transport.connect(username=self.username, password=self.pwd)
        self.__transport = transport

    def ssh(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, username=self.username, password=self.pwd)
        return ssh

    def close(self):
        self.__transport.close()

    def upload(self, remoteDir):
        from fhomeserver.settings import BASE_DIR
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        ssh = self.ssh()
        system = sys.platform

        print("{}开始更新".format(self.host))
        print()
        for file in file_list:
            file_path = os.path.join(BASE_DIR, file)            # 文件路径
            if system == 'win32':
                file = file.replace("\\", "/")

            file_name = file.split('/')[-1]                     # 文件名
            file_dir = '/'.join(file.split('/')[:-1])           # 所属文件夹
            server_file_path = remoteDir + file_dir + "/"       # 对应到服务器上的文件夹

            ssh.exec_command('mkdir -p ' + server_file_path)    # 创建文件夹，如果已经存在不会创建

            print("正在上传" + file + "  --->  " + self.host)
            sftp.put(file_path, server_file_path + file_name)   # 上传
            print(file + "上传成功。")
            time.sleep(0.5)


        print("{}已完成更新".format(self.host))
        print("")
        ssh.close()

    def run(self, remoteDir):
        self.connect()
        time.sleep(1)
        self.upload(remoteDir)
        self.close()


def update():
    r = local.LocalClient(os.getcwd())
    current_version = r.info()['commit_revision']
    print("当前版本revision:{}".format(current_version))
    print("正在获取更新。。。")
    a = os.popen("svn update").read()
    print(a)
    reg1 = 'fmodel\\s*\\w*\\W*\\S*'
    regCom1 = re.compile(reg1)
    pathList1 = re.findall(regCom1, a)
    reg2 = 'adminsite\\s*\\w*\\W*\\S*'
    regCom2 = re.compile(reg2)
    pathList2 = re.findall(regCom2, a)

    pathList = pathList1 + pathList2

    return pathList


file_list = update()


dep1 = Deploy(host='', username='', pwd='')
remoteDir1 = '/app/project/'      # 该服务器上项目对应的文件夹，最后一定要加上"/"
dep1.run(remoteDir1)


dep2  = Deploy(host='',username='', pwd='')
remoteDir2 = '/apps/project/'     # 该服务器上项目对应的文件夹，最后一定要加上"/"
dep2.run(remoteDir2)

