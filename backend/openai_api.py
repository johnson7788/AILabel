#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2022/8/18 13:30
# @File  : baidu_sentiment_api.py
# @Author: 
# @Desc  : Openai的API调用
import os
import time
import requests
import json
import httpx
import random
from openai import OpenAI
import hashlib
import logging
from flask import Flask, request, jsonify, abort
app = Flask(__name__)
# 日志保存的路径，保存到当前目录下的logs文件夹中
log_path = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_path):
    os.makedirs(log_path)
logfile = os.path.join(log_path, "openai_api.log")
# 日志的格式
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s -  %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(logfile, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

api_key = "sk-"
assert api_key, "请先设置API_KEY"
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(
        proxy="http://127.0.0.1:7890",
    ),
)

def openai_api(data, time_sleep=0.5, temperature=0.5,usecache=True):
    """
    调用openai的接口
    :param data: 输入的数据
    :param time_sleep: 每次调用的间隔
    """
    data_completions = []
    for idx, one in enumerate(data):
        prompt = one["prompt"]
        context = one.get('text', "")
        if not context:
            context = one.get('context', "")
        # 如果以前有缓存的结果，就直接不预测了，首先计算md5
        md5 = cal_md5(prompt + context)
        # 如果有缓存的结果，就直接加到结果中
        cache_result = load_cache(md5)
        if cache_result and usecache:
            logging.info(f"第{idx}条数据的是有缓存结果的，不用预测了")
            data_completions.append(cache_result)
            continue
        if context:
            content = f"{prompt}\n{context}"
        else:
            content = prompt
        logging.info(f"输入的数据的prompt: {prompt}, 文本上下文是: {context}")
        completions = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content
                },
            ],
            model="gpt-4o-mini",
            temperature=temperature,
            stream=False
        )
        one_data = {
            "input_prompt": prompt,
            "input_text": content,
            "result": completions
        }
        logging.info(f"第{idx}条数据的预测结果是: {completions}")
        data_completions.append(one_data)
        # 休眠一下
        cache_predict(data=one_data, md5=md5)
        logging.info(f"休眠{time_sleep}秒")
        time.sleep(time_sleep)
    return data_completions
def openai_raw_message(messages, tools=None, temperature=0.5, usecache=True,model="gpt-4o-mini"):
    """
    直接给openai发送组装好的messages信息
    :param data: 输入的数据
    :param time_sleep: 每次调用的间隔
    """
    logging.info(f"输入的数据的messages: {messages}, 使用的模型是: {model}")
    md5 = cal_md5(messages)
    cache_result = load_cache(md5, prefix="openai.json")
    if cache_result and usecache:
        logging.info(f"有缓存结果，不用预测了")
        return cache_result
    if tools:
        completions = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            tools=tools,
            stream=False
        )
    else:
        completions = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            stream=False
        )
    choices = completions.choices[0]
    content = choices.message.content if choices.message.content else ""
    function_call = choices.message.function_call if choices.message.function_call else ""
    tools_calls = choices.message.tool_calls if choices.message.tool_calls else []
    role = choices.message.role if choices.message.role else ""
    finish_reason = choices.finish_reason if choices.finish_reason else ""
    if tools_calls:
        new_calls = []
        for tool_call in tools_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments
            tool_id = tool_call.id
            new_calls.append({"name": name, "arguments": arguments, "id": tool_id})
        tools_calls = new_calls
    one_data = {
        "message": messages,
        "result": {
            "content": content,
            "function_call": function_call,
            "tool_calls": tools_calls,
            "role": role,
            "finish_reason": finish_reason,
            "model": completions.model,
        }
    }
    logging.info(f"预测结果是: {completions}")
    # 休眠一下
    cache_predict(data=one_data, md5=md5, prefix="openai.json")
    return one_data

def load_cache(md5, cache_dir="cache", prefix="json"):
    """
    如果有缓存的结果，就直接返回，否则返回None
    """
    filename = f"{md5}.{prefix}"
    filepath = os.path.join(cache_dir, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logging.error(f"加载缓存失败: {e}")
            return None
    else:
        return None

def cache_predict(data, md5, cache_dir="cache",prefix="json"):
    """
    缓存预测结果
    :param open_result: dict
    :type open_result:
    :return:
    :rtype:
    """
    filename = f"{md5}.{prefix}"
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    filepath = os.path.join(cache_dir, filename)
    # 保存到
    with open(filepath, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("缓存文件到{}".format(filepath))

def cache_data(data, cache_dir="cache", prefix="json"):
    """
    通用的保存结果的函数
    """
    md5 = data.get("md5")
    assert md5, f"数据没有md5，这是不对的: {data}"
    filename = f"{md5}.{prefix}"
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    filepath = os.path.join(cache_dir, filename)
    # 保存到
    with open(filepath, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("缓存文件到{}".format(filepath))

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

@app.route("/api/openai", methods=['POST'])
def openai_predict():
    """
    Args: 预测openai的接口
    """
    jsonres = request.get_json()
    # 可以预测多条数据
    data = jsonres.get('data')
    usecache = jsonres.get('usecache', True) # 默认预测过的就不再次预测了
    if not data:
        return jsonify("参数data不能为空"), 202
    # 检查数据
    for idx, one in enumerate(data):
        prompt = one.get('prompt')
        if not prompt:
            return jsonify(f"第{idx}条数据的提示语参数prompt不能为空"), 202
    #现在实体的长度大于一定长度
    logging.info(f"输入数据共: {len(data)} 条，输入数据是:{data}")
    result = openai_api(data, usecache=usecache)
    logging.info(f"预测的结果是:{result}")
    return jsonify(result)

@app.route("/api/message", methods=['POST'])
def openai_message():
    """
    Args: 预测openai的接口
    message的格式是：
    message = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "请对比商品资生堂随肌应变遮瑕液和资生堂随肌应变遮瑕膏？"
        }
    ]
    """
    jsonres = request.get_json()
    # 可以预测多条数据
    message = jsonres.get('message')
    temperature = jsonres.get('temperature',0.5)
    usecache = jsonres.get('usecache', True) # 默认预测过的就不再次预测了
    tools = jsonres.get('tools') # 默认预测过的就不再次预测了
    model = jsonres.get('model_name',"gpt-4o-mini") # 默认预测过的就不再次预测了
    # 检查数据
    result = openai_raw_message(messages=message, tools=tools, temperature=temperature,usecache=usecache,model=model)
    logging.info(f"预测的结果是:{result}")
    return jsonify(result)

@app.route("/ping", methods=['GET','POST'])
def ping():
    """
    测试
    :return:
    :rtype:
    """
    return jsonify("Pong")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4636, debug=False, threaded=True)