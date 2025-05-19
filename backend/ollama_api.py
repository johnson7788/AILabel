#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  :
# @File  :
# @Author:
# @Desc  : ollama操作
import logging
import os, re
import time

log_path = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_path):
    os.makedirs(log_path)
logfile = os.path.join(log_path, "ollama.log")
# 日志的格式
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s -  %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(logfile, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

import json
import datetime
import shutil
import requests
import aiohttp  # 使用 aiohttp 库进行异步请求
from fastapi import FastAPI, UploadFile, Form, File, Body, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing_extensions import Annotated
from typing import List
from enum import Enum
from io import BytesIO
import subprocess
import uvicorn
import asyncio
import numpy as np
from rich.pretty import pprint
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OllamaOperate(object):
    def __init__(self):
        self.hugging_download_log = "hugging_download.log"
        self.ollama_download_log = "ollama_download.log"

    async def huggingface_download_model(self, model_name):
        """
        下载模型
        Args:
            model_name ():eg: "Qwen/Qwen2.5-32B-Instruct-GGUF"
        Returns:
        """
        start_time = time.time()
        command = [
            "huggingface-cli", "download", model_name, "--local-dir", ".", "--local-dir-use-symlinks", "False"
        ]
        with open(self.hugging_download_log, "a") as log_file:  # 追加模式打开日志文件
            while True:
                try:
                    # 执行下载命令，将输出和错误重定向到日志文件
                    result = subprocess.run(command, stdout=log_file, stderr=log_file, check=True)
                    print("文件下载成功")
                    break  # 下载成功后退出循环
                except subprocess.CalledProcessError as e:
                    print("下载中断，正在重新尝试...")
                    time.sleep(5)  # 可选：等待几秒后再重试
        print(f"花费时间: {time.time() - start_time}秒")
        return True

    async def read_download_log(self, logtype="hugging"):
        """
        读取下载日志，返回最后200条日志
        Returns:
        """
        if logtype == "hugging":
            log_file = self.hugging_download_log
        elif logtype == "ollama":
            log_file = self.ollama_download_log
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
        else:
            lines = []
        log = "\n".join(lines[-200:])
        return log

    async def ollama_download_model(self, model_name):
        """
        使用ollama下载模型
        Args:
            model_name ():eg: "qwen2.5:32b-instruct-fp16"
        Returns:
        """
        start_time = time.time()
        command = [
            "/usr/local/bin/ollama", "pull", model_name
        ]
        with open(self.ollama_download_log, "a") as log_file:  # 追加模式打开日志文件
            while True:
                try:
                    # 执行下载命令，将输出和错误重定向到日志文件
                    result = subprocess.run(command, stdout=log_file, stderr=log_file, check=True)
                    print("文件下载成功")
                    break  # 下载成功后退出循环
                except subprocess.CalledProcessError as e:
                    print("下载中断，正在重新尝试...")
                    time.sleep(5)  # 可选：等待几秒后再重试
        print(f"花费时间: {time.time() - start_time}秒")
        return True

class Item(BaseModel):
    name: str #模型名称

@app.post("/api/hugging_download")
async def hugging_download_api(item: Item, background_tasks: BackgroundTasks):
    name = item.name
    # 把处理任务放入后台任务队列
    background_tasks.add_task(ollama_instance.huggingface_download_model, name)
    return {"code": 0, "msg": "success", "data": "请求已收到，正在处理中"}

@app.get("/api/hugging_log")
async def hugging_log_api():
    # 把处理任务放入后台任务队列
    hugging_log = ollama_instance.read_download_log(logtype="hugging")
    return {"code": 0, "msg": "success", "data": hugging_log}

@app.post("/api/ollama_download")
async def ollama_download_api(item: Item, background_tasks: BackgroundTasks):
    name = item.name
    # 把处理任务放入后台任务队列
    background_tasks.add_task(ollama_instance.ollama_download_model, name)
    return {"code": 0, "msg": "success", "data": "请求已收到，正在处理中"}

@app.get("/api/ollama_log")
async def ollama_log_api():
    # 把处理任务放入后台任务队列
    ollama_log = ollama_instance.read_download_log(logtype="ollama")
    return {"code": 0, "msg": "success", "data": ollama_log}

@app.api_route("/ping", methods=["GET", "POST"])
async def root(request: Request):
    return "Pong"

if __name__ == '__main__':
    ollama_instance = OllamaOperate()
    uvicorn.run(app, host='0.0.0.0', port=5316)
