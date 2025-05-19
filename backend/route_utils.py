#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/8/5 15:40
# @File  : route_utils.py
# @Author: 
# @Desc  : 一些工具函数

import os
import re
import tarfile
import requests
import json
import shutil
import subprocess
import time
import pickle
import logging
from functools import wraps
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tika
from tika import parser as tikaParser
TIKA_SERVER_JAR = "file:////home/wac/johnson/johnson/paper/tika-server.jar"
os.environ['TIKA_SERVER_JAR'] = TIKA_SERVER_JAR

def check_command_exists(command):
    return shutil.which(command) is not None

def cal_md5(content):
    """
    计算content字符串的md5
    :param content:
    :return:
    """
    # 使用encode
    content = str(content)
    result = hashlib.md5(content.encode())
    # 打印hash
    md5 = result.hexdigest()
    return md5

def cache_decorator(func):
    """
    cache从文件中读取, 当func中存在usecache时，并且为False时，不使用缓存
    Args:
        func ():
    Returns:
    """
    cache_path = "cache" #cache目录
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 将args和kwargs转换为哈希键， 当装饰类中的函数的时候，args的第一个参数是实例化的类，这会通常导致改变，我们不想检测它是否改变，那么就忽略它
        usecache = kwargs.get("usecache", True)
        if "usecache" in kwargs:
            del kwargs["usecache"]
        if len(args)> 0:
            if isinstance(args[0],(int, float, str, list, tuple, dict)):
                key = str(args) + str(kwargs) + func.__name__
            else:
                # 第1个参数以后的内容
                key = str(args[1:]) + str(kwargs) + func.__name__
        else:
            key = str(args) + str(kwargs) + func.__name__
        # 变成md5字符串
        key_file = os.path.join(cache_path, cal_md5(key) + "_cache.pkl")
        # 如果结果已缓存，则返回缓存的结果
        if os.path.exists(key_file) and usecache:
            # 去掉kwargs中的usecache
            print(f"函数{func.__name__}被调用，缓存被命中，使用已缓存结果，对于参数{key}, 读取文件:{key_file}")
            with open(key_file, 'rb') as f:
                result = pickle.load(f)
                return result
        result = func(*args, **kwargs)
        # 将结果缓存到文件中
        # 如果返回的数据是一个元祖，并且第1个参数是False,说明这个函数报错了，那么就不缓存了，这是我们自己的一个设定
        if isinstance(result, tuple) and result[0] == False:
            print(f"函数{func.__name__}被调用，返回结果为False，对于参数{key}, 不缓存")
        else:
            with open(key_file, 'wb') as f:
                pickle.dump(result, f)
            print(f"函数{func.__name__}被调用，缓存未命中，结果被缓存，对于参数{key}, 写入文件:{key_file}")
        return result

    return wrapper

def read_file_content(file_path):
    assert os.path.exists(file_path), f"给定文件不存在: {file_path}"
    tika_jar_path = TIKA_SERVER_JAR.replace('file:///', '')
    assert os.path.exists(tika_jar_path), "tika jar包不存在"
    tika.initVM()
    parsed = tikaParser.from_file(file_path)
    content_text = parsed["content"]
    content = content_text.split("\n")
    return content

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, source_dir, backup_dir, max_file_size=20 * 1024 * 1024):
        self.max_file_size = max_file_size #超过某个大小的文件，不进行备份
        self.source_dir = source_dir
        assert os.path.isdir(source_dir), "Source directory does not exist"
        self.last_hash = self.hash_directory(source_dir)
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

    def hash_directory(self, source_dir):
        hasher = hashlib.md5()
        for root, _, files in os.walk(source_dir):
            for file in sorted(files):
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    buf = f.read()
                    hasher.update(buf)
        return hasher.hexdigest()

    def has_changed(self):
        current_hash = self.hash_directory(self.source_dir)
        if current_hash != self.last_hash:
            self.last_hash = current_hash
            return True
        return False

    def create_backup(self):
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_name)
        with tarfile.open(backup_path, "w:gz") as tar:
            self.add_files(tar, self.source_dir)
        return backup_path

    def add_files(self, tar, directory):
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) <= self.max_file_size:
                    arcname = os.path.relpath(file_path, start=self.source_dir)
                    tar.add(file_path, arcname=arcname)
    def cleanup_backups(self, keep=5):
        backups = sorted([f for f in os.listdir(self.backup_dir) if f.startswith('backup_')], reverse=True)
        for backup in backups[keep:]:
            os.remove(os.path.join(self.backup_dir, backup))

@cache_decorator
def local_chat(prompt, question):
    """
    测试chat接口
    :return:
    """
    url = f"http://127.0.0.1:5556/api/chat"
    # 提交form格式数据
    headers = {'content-type': 'application/json'}
    # 提交form格式数据
    data = {"prompt": prompt,"llm":"llama3-70B","tools":[], "messages": [{'content': question, 'role': 'user'}]}
    r = requests.post(url, data=json.dumps(data),headers=headers)
    res = r.json()
    print(json.dumps(res, indent=4, ensure_ascii=False))
    return res

def ssh_command(msg, command, exp=None, ignore=False, return_out=False, return_code=False, print_command=True, return_outcode=False, streaming=False):
    """
    运行ssh命令，如果返回不为0，那么报exception
    :param msg: 打印消息
    :param command: ssh 命令
    :param exp: exception的消息
    :param ignore: 忽略错误错误消息
    :return:
    """
    if print_command:
        print('*' * 40)
    if print_command:
        # 只有替换了的命令，并且需要打印命令时，才输出这条日志
        print(f"{command}")
    if exp is None:
        exp = msg + "错误"
    if streaming:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        def stream_output():
            for line in process.stdout:
                yield line.strip()
            process.stdout.close()
            process.wait()

        if return_outcode:
            return stream_output(), process.returncode
        else:
            return stream_output()
    if return_out or return_outcode:
        code, out = subprocess.getstatusoutput(command)  #运行结束后返回命令行输出，不能边运行边输出
    else:
        code = os.system(command)  #可以边运行，边输出命令行输出
        out = '打印到console上了'
    if code != 0 and not ignore and not return_code:
        logging.info(f"返回的code不为0，可以设置ignore参数忽略，如果仅需要输出code或消息")
        raise Exception(exp)
    else:
        if code != 0:
            if not ignore:
                logging.info(f"运行完成，但是返回CODE不为0，请检查! {msg}")
        else:
            if print_command:
                logging.info(f"运行成功! {msg}")
    if return_outcode:
        return code, out
    elif return_code:
        return code
    else:
        return out


if __name__ == "__main__":
    source_dir = '/Users/admin/cache'
    backup_dir = '/tmp/'
    backup_instance = ChangeHandler(source_dir,backup_dir)
    # if backup_instance.has_changed():
    #     backup_path = backup_instance.create_backup()
    #     backup_instance.cleanup_backups()
    #     print({"message": "Backup created", "backup": backup_path})
    # else:
    #     print({"message": "No changes detected, no backup created"})
