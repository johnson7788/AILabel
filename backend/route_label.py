"""
这段代码是工具注册的部分，通过注册工具，让模型实现工具调用
代码来自ChatGLM3/tools_using_demo/tool_register.py
"""
import os
import logging
if not os.path.exists("logs"):
    os.makedirs("logs")
logfile = "logs/label.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(logfile, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

import time
import random
import hashlib
import datetime
from datetime import timedelta
import json
import re
import importlib
import inspect
import requests
import subprocess
import traceback
from openai import OpenAI
from copy import deepcopy
from pprint import pformat
from types import GenericAlias
from typing import get_origin, Annotated
from neo4j_ceshi import FoodNeo4j
from mongo_client import MongoDBManager
from py2neo import Graph, Node, Relationship
from flask import Flask, request, jsonify, abort, render_template, Response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from functools import wraps
from flask import Blueprint

bp = Blueprint('label', __name__)

_TOOL_HOOKS = {}  # 工具名称对应函数
_TOOL_DESCRIPTIONS = {}  # 工具名称对应工具参数

# 注册工具
def register_tool(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")

        typ, (description, required) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__
        if not isinstance(description, str):
            raise TypeError(f"Description for `{name}` must be a string")
        if not isinstance(required, bool):
            raise TypeError(f"Required for `{name}` must be a bool")
        if not required:
            default_value = param.default
        else:
            default_value = ""
        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
            "required": required,
            "default": default_value  # 默认值
        })

    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "params": tool_params
    }

    print("[registered tool] " + pformat(tool_def))
    _TOOL_HOOKS[tool_name] = func
    _TOOL_DESCRIPTIONS[tool_name] = tool_def

    return func

def modify_tool_description(tool_name, meta_dict):
    """
    修改_TOOL_DESCRIPTIONS
    Args:
        tool_name (): 工具名称
        meta_dict (): dict, 基本信息
    Returns:
    """
    tool_def = _TOOL_DESCRIPTIONS.get(tool_name)
    if tool_def is None:
        return False
    tool_def.update(meta_dict)
    _TOOL_DESCRIPTIONS[tool_name] = tool_def
    return True

# 导入目录下所有 Python 文件并注册装饰器
def import_and_register_tools(directory):
    for filename in os.listdir(directory):
        # 确保是 Python 文件
        if filename.endswith(".py"):
            module_name = filename[:-3]  # 去除扩展名
            module_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # 遍历模块中的成员，如果是函数并且没有被装饰过，则应用装饰器
            finded_tool_names = [] # 这个文件可能包含的工具，可能有多个，但是不建议，应该每个文件只有1个函数
            for name, obj in vars(module).items():
                if callable(obj) and hasattr(obj, '__module__'):
                    if obj.__module__ == module_name:
                        setattr(module, name, register_tool(obj))
                        finded_tool_names.append(name)
            assert len(finded_tool_names) == 1, f"{filename} 文件中包含0个货多个工具函数，请确保每个文件只有一个工具函数"
            for name, obj in vars(module).items():
                if name == "tool_meta":
                    print(f"工具{name}有基本的meta信息，即将录入")
                    modify_tool_description(finded_tool_names[0], obj) # 只录入第1个工具的基本信息

# 导入tools目录下所有文件并注册
import_and_register_tools("tools")

def check_and_convert_tool_parameters(tool_name: str, tool_params: dict):
    """
     检查工具参数是否符合要求, 如果不符合，进行强制转化
     Args:
         tool_name ():
         tool_params ():
     Returns:
         status, new_params
     """
    tool_def = _TOOL_DESCRIPTIONS.get(tool_name)
    if tool_def is None:
        return False, f"对应的工具{tool_name}没有找到参数约束信息，请检查"
    params_def = tool_def.get("params")
    if params_def is None:
        # 如果函数中没有定义参数要求，那么直接返回原始的参数
        return True, tool_params
    # 如果tool_params中某个值为空，说明是默认值，会被剔除调
    logging.info(f"工具{tool_name}传入的总共的参数个数是: {len(tool_params)}")
    tool_params = {k: v for k, v in tool_params.items() if v != ""}
    logging.info(f"过滤掉空值后剩余的参数个数是: {len(tool_params)}")
    # 名称到详细结果的映射
    params_def_dict = {param.get("name"): param for param in params_def}
    for one_params_name, one_params_def in params_def_dict.items():
        one_params_required = one_params_def["required"]
        if one_params_required:
            if one_params_name not in tool_params:
                return False, f"参数{one_params_name}是必填项，但是没有传入，请检查"
    new_tool_params = {}
    for one_params_name, one_params_value in tool_params.items():
        if one_params_name not in params_def_dict:
            return False, f"传入的参数名{one_params_name}在工具{tool_name}中没有定义，请检查传入的参数名称是否正确"
        one_params_def = params_def_dict.get(one_params_name)
        one_params_type = one_params_def["type"]
        current_params_type = type(one_params_value).__name__
        if current_params_type != one_params_type:
            logging.warning(f"注意，传入的参数{one_params_name}的类型{current_params_type}和定义的类型{one_params_type}不一致，开始强制转化")
            if one_params_type == "int":
                one_params_value = int(one_params_value)
            elif one_params_type == "float":
                one_params_value = float(one_params_value)
            elif one_params_type == "bool":
                one_params_value = bool(one_params_value)
            elif one_params_type == "str":
                one_params_value = str(one_params_value)
            elif 'tuple' in one_params_type:
                one_params_value = tuple(one_params_value)
            elif one_params_type == "list":
                one_params_value = json.loads(one_params_value)
                if not isinstance(one_params_value, list):
                    return False, f"{one_params_name}传入的参数类型{current_params_type}经过Json加载后仍然不是预期的数据类型list，请检查传入的参数值是否正确"
            elif one_params_type == "dict":
                one_params_value = json.loads(one_params_value)
                if not isinstance(one_params_value, dict):
                    return False, f"{one_params_name}传入的参数类型{current_params_type}经过Json加载后仍然不是预期的数据类型dict，请检查传入的参数值是否正确"
            else:
                return False, f"{one_params_name}传入的参数类型{current_params_type}不在预期范围内，请检查传入的参数值是否正确"
        new_tool_params[one_params_name] = one_params_value
    return True, new_tool_params

def dispatch_tool(tool_name: str, tool_params: dict) -> str:
    """
    调用工具，并返回工具的执行结果
    Args:
        tool_name ():
        tool_params ():
    Returns:
    调用工具时，工具返回的meta信息不是必须的，如果不存在meta信息，返回一个空的meta
    {msg: 返回的消息, need_summary: 是否需要生成总结，如果需要就会使用该msg消息生成最终结果, status: bool值，工具是正常还是异常, "meta": {}一些元数据，例如可以绘图和展示等}
    """
    if tool_name not in _TOOL_HOOKS:
        return {"msg": f"工具 `{tool_name}` 没有找到，请确认工具的名称是正确的", "need_summary": False, "status": False, "meta": {}}
    tool_call = _TOOL_HOOKS[tool_name]
    if isinstance(tool_params, str):
        try:
            tool_params = json.loads(tool_params)
        except json.JSONDecodeError:
            return {"msg": f"工具 `{tool_name}` 参数不是合法的JSON格式，请检查参数是否正确", "need_summary": False, "status": False, "meta": {}}
    status, new_tool_params = check_and_convert_tool_parameters(tool_name, tool_params)
    if not status:
        return {"msg": new_tool_params, "need_summary": False, "status": False, "meta": {}}
    try:
        ret = tool_call(**new_tool_params)
        if "meta" not in ret:
            ret["meta"] = {}
        return ret
    except:
        msg = traceback.format_exc()
        return {"msg": msg, "need_summary": True, "status": False, "meta": {}}

def get_tools(js_type=True) -> dict:
    """
    Python的list：这是一个有序的元素集合，元素可以是任何类型，对应于JavaScript中的Array。
    Python的tuple：这是一个有序的元素集合，但元素一旦初始化就无法修改，JavaScript并没有直接的对应，但Array或对象可以部分模仿tuple的功能。
    Python的dict：这是一个关联数组，即一个键值对集合，对应于JavaScript中的Object。
    Python的set：这是一个无序的独特元素集合，对应于JavaScript的Set。
    JavaScript的Map是一种类似于对象的数据类型，它允许键可以是任何类型。Python中没有直接对应的数据类型，但可以使用字典（只能有可哈希的键）或一个包含两元素元组的列表来模仿类似的功能。
    Python的zip是一个内置函数，它接受一系列可迭代对象并返回元组的迭代器，每个元组中的元素来自所有输入迭代器的相同位置。JavaScript没有直接的对应，但可以用Array.prototype.map()方法和解构赋值来模仿类似的功能。
    Python的None对应JavaScript的null或undefined，表示没有值或没有定义
    js_type: 转化成js的类型
    """
    # python类型映射到js类型
    param_type_dict = {
        "int": "number",
        "str": "string",
        "float": "number",
        "bool": "boolean",
        "list": "Array",
        "tuple": "Array",
        "dict": "Object",
        "set": "Set",
        "None": "null",
        "tuple[int, int]": "Array<number, number>",
    }
    tools_descripion = deepcopy(_TOOL_DESCRIPTIONS)
    if js_type:
        for tool_name, tool_info in tools_descripion.items():
            params = tool_info["params"]
            for idx, param_info in enumerate(params):
                param_type = param_info.get("type")
                js_param_type = param_type_dict[param_type]
                params[idx]["type"] = js_param_type
            tools_descripion[tool_name]["params"] = params
    return tools_descripion

# 定义工具和注册工具
@register_tool
def random_number_generator(
        seed: Annotated[int, 'The random seed used by the generator', True],
        range: Annotated[tuple[int, int], 'The range of the generated numbers', True],
) -> int:
    """
    给出2个整数之间的获取随机整数
    """
    if not isinstance(seed, int):
        raise TypeError("Seed must be an integer")
    if (not isinstance(range, tuple) and not isinstance(range, list)):
        raise TypeError("Range must be a tuple")
    if not isinstance(range[0], int) or not isinstance(range[1], int):
        raise TypeError("Range must be a tuple of integers")
    number = random.Random(seed).randint(*range)
    return {"msg": number, "need_summary": True, "status": True}


@register_tool
def food_information_extraction(
        text: Annotated[str, '一条文本', True],
) -> str:
    """
    对给出的一条食品相关的文本进行知识抽取，抽出食物相关知识和对其进行情感分析
    """
    status, msg, meta = food_instance.sentiment_extract_model(text)
    if status:
        return {"msg": msg, "need_summary": True, "status": True, "meta": meta}
    else:
        return {"msg": msg, "need_summary": True, "status": False, "meta": meta}

@register_tool
def food_neo4j_query(
        content: Annotated[str, '要搜索的内容', True],
        node_names: Annotated[list, '要搜索的节点名称,可以不提供，默认搜索所有可能节点', False] = ["all"],
        topk: Annotated[int, '返回的最相关的结果个数，默认是1个', False] = 1,
) -> str:
    """
    搜索食品领域的知识图谱，节点名称可以是食品，口感，馅料，包装，便捷程度，场景，皮，味道，气味，外形，烹饪方法，质量缺陷，服务，价格中的1个或者几个
    """
    status, msg, meta = food_instance.query_by_search(content,node_names,topk)
    if status:
        return {"msg": msg, "need_summary": True, "status": True, "meta": meta}
    else:
        return {"msg": msg, "need_summary": True, "status": False, "meta": meta}

@register_tool
def food_neo4j_stats() -> str:
    """
    返回当前食品领域的知识图谱的统计结果
    """
    status, msg, meta = food_instance.count_kg_scope()
    if status:
        return {"msg": msg, "need_summary": True, "status": True, "meta": meta}
    else:
        return {"msg": msg, "need_summary": True, "status": False, "meta": meta}


@register_tool
def query_neo4j(
        cql: Annotated[str, 'neo4j的查询cql', True],
) -> str:
    """
    根据提供的cql语句查询neo4j数据库
    """
    logging.info(f"收到要执行cql: {cql}")
    try:
        graph = get_graph()
    except:
        import traceback
        ret = "连接neo4j数据库错误，请联系管理员\n" + traceback.format_exc()
        logging.error(ret)
        return {"msg": ret, "need_summary": True, "status": False}
    try:
        res = graph.run(cql)
        logging.info(f"执行cql成功: {cql}")
        return {"msg": res, "need_summary": True, "status": True}
    except Exception as e:
        import traceback
        res = f"执行cql报错: : {cql}，请检查, 错误是: {e}\n" + + traceback.format_exc()
        logging.error(res)
        return {"msg": res, "need_summary": True, "status": False}


@register_tool
def determine_advertisement(
        comment: Annotated[str, '一条评论数据', True],
) -> str:
    """
    判断给出的评论是否是广告
    """
    if not isinstance(comment, str):
        raise TypeError("评论数据必须是字符串格式")

    try:
        params = {'data': [comment]}
        url = f"http://192.168.50.139:3326/api/adfilter_predict"
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=json.dumps(params), timeout=360)
        result = r.json()
        one_result = result[0]
        res = one_result[0]
        # 修改下标签
        if res == "正常":
            ret = "是正常评论"
        else:
            ret = "是广告水军"
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error: 执行判断广告的接口错误!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

@register_tool
def today_date(
) -> str:
    """
    获取现在的日期，时间，和星期
    """
    today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    # 获取当前日期
    today_date = datetime.date.today()
    # 获取星期几（0是星期一，6是星期日）
    weekday = today_date.weekday()
    # 创建一个列表，用于将数字映射到星期
    days = ["一", "二", "三", "四", "五", "六", "日"]
    ret = f"今天是: {today}, 星期{days[weekday]}"
    return {"msg": ret, "need_summary": True, "status": True}


@register_tool
def get_ip_location(
        ip_address: Annotated[str, 'ip地址需要提供', True],
) -> str:
    """
    根据提供的ip地址，查询ip地址的位置信息
    """

    def validate_ip(ip):
        """验证IPv4地址的有效性"""
        # 创造一个4位0-9，0-255的正则表达式
        pattern = re.compile(
            "^(([0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\\.){3}([0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])$"
        )

        if pattern.match(ip):
            return True
        else:
            return False

    if not validate_ip(ip_address):
        raise TypeError("ip地址格式错误，请检查后重新输入")
    try:
        resp = requests.get(f"https://www.7udh.com/ipinfo.php?ip={ip_address}")
        resp.raise_for_status()
        ret_text = resp.text
        last_line = ret_text.splitlines()[-1]
        last_line_json = json.loads(last_line)
        ret = last_line_json["ipinfo"]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


@register_tool
def search_memes(
        keyword: Annotated[str, '搜索表情包的关键词', True],
) -> str:
    """
    根据关键词搜索表情包,返回图片url列表
    """
    try:
        resp = requests.get(f"https://api.tangdouz.com/a/biaoq.php?return=json&nr={keyword}")
        resp.raise_for_status()
        resp_json = resp.json()
        # 获取前3张图片
        resp_json_top3 = resp_json[:3]
        ret = [i["thumbSrc"] for i in resp_json_top3]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


@register_tool
def generate_avatar(
) -> str:
    """
    生成1张头像图片,返回本地图片地址
    """
    try:
        resp = requests.get(f"http://api.tangdouz.com/wz/tmtx.php?q=3336530155")
        resp.raise_for_status()
        image_path_name = "data/avatar.png"
        with open(image_path_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        ret = image_path_name
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

@register_tool
def weixin_block(
        url: Annotated[str, '要检测的网址', True],
) -> str:
    """
    检测提供的网址是否被微信拦截了
    """
    try:
        resp = requests.get(f"https://www.7udh.com/jiance/wechat.php?url={url}")
        resp.raise_for_status()
        resp_json = resp.json()
        ret = resp_json["msg"]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


@register_tool
def generate_qrcode(
        text: Annotated[str, '文本内容', True],
) -> str:
    """
    根据文本内容生成一个二维码图片，返回本地图片地址
    """
    try:
        resp = requests.get(f"https://api.7trees.cn/qrcode/?data={text}")
        resp.raise_for_status()
        image_path_name = "data/qrcode.png"
        with open(image_path_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        ret = image_path_name
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

@register_tool
def get_car_price(
        car_name: Annotated[str, '汽车的名称', True],
) -> str:
    """
    给定汽车的名称，获取汽车的价格
    """
    try:
        random_price = random.randint(10000, 100000)
        prices_data = {
            "Tang": "$20000",
            "Song": "$25000",
        }
        ret = prices_data.get(car_name,f"${random_price}")
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

# key获取地址： https://api.linhun.vip/doc/wbrd.html#
@register_tool
def weibo_hot_search(
) -> str:
    """
    返回微博热搜
    """
    apiKey = "c12312115159-4925099071c-dad899dc623"
    try:
        resp = requests.get(f"https://api.linhun.vip/api/wbrd?text&apiKey={apiKey}")
        resp.raise_for_status()
        ret = resp.text
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


# key获取地址： https://api.aa1.cn/doc/today_history.html
@register_tool
def today_history(
) -> str:
    """
    返回今天的历史事件，返回列表
    """
    try:
        resp = requests.get(f"https://tools.mgtv100.com/external/v1/today_history")
        resp.raise_for_status()
        resp_json = resp.json()
        ret = resp_json["data"]["data"][:3]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


@register_tool
def search_movie(
        keyword: Annotated[str, '关键字', True],
) -> str:
    """
    根据关键字搜索电影,返回列表
    """
    try:
        resp = requests.get(f"https://lj.sgai.cc/maren-master/baidu.php?text={keyword}")
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json.get("msg"):
            ret = resp_json["msg"]
        else:
            ret = resp_json["list"][:3]
        return {"msg": ret, "need_summary": True, "status": True}

    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}


@register_tool
def wangzhe_role(
        name: Annotated[str, '人物名称,eg:瑶', True],
) -> str:
    """
    根据王者荣耀英雄名称获取该英雄与其所有皮肤的无水印海报
    """
    try:
        resp = requests.get(f"http://kloping.top/api/get/pvp-skin?name={name}")
        resp.raise_for_status()
        ret = resp.json()
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

@register_tool
def perfume_knowledge(
        question: Annotated[str, '香水问题', True],
) -> str:
    """
    这个工具可以回答任何香水相关的知识。
    """
    try:
        def get_one_kbid(kbname):
            url = f"http://192.168.50.189:8777/api/local_doc_qa/list_knowledge_base"
            headers = {'content-type': 'application/json'}
            data = {"user_id": "zzp"}
            # 提交form格式数据
            r = requests.post(url, data=json.dumps(data), headers=headers)
            res = r.json()
            data = res["data"]
            assert len(data) >0 ,f"还没有创建知识库，所以无法获取知识库的id"
            name2id =  {item["kb_name"]:item["kb_id"] for item in data}
            kb_id = name2id.get(kbname)
            assert kb_id is not None, f"知识库{kbname}不存在"
            return kb_id
        kb_id = get_one_kbid(kbname="english")
        url = f"http://192.168.50.189:8777/api/local_doc_qa/local_doc_chat"
        headers = {'content-type': 'application/json'}
        data = {"user_id":"zzp", "kb_ids": [kb_id],"question":question}
        # 提交form格式数据
        r = requests.post(url, data=json.dumps(data), headers=headers)
        res = r.json()
        ret = res["response"]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error encountered while fetching data!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}

@register_tool
def operate_mtdnn_model(action: Annotated[str, '要执行的任务命令，可选start，stop, status, restart', True],
                        host: Annotated[str, '在哪个机器上执行,支持主机名称139,169,179,189,209', True]) -> str:
    """
    操作mtdnn模型，可以选择不同的主机，使用不同的操作，包括启动，停止，当前状态，和重启
    """
    if action not in ["start","stop","status","restart"]:
        return {"msg": "您使用的参数action的值必须是start，stop，status，restart中的1个", "need_summary": True, "status": False}
    task_name = "dem8-mtdnn-3326"
    host_mapper = {
        "139": "192.168.50.139",
        "169": "192.168.50.169",
        "179": "192.168.50.179",
        "189": "192.168.50.189",
        "209": "192.168.50.209",
    }
    host_ip = host_mapper.get(host)
    if not host_ip:
        return {"msg": f"您输入的主机名称{host}不在可选列表中", "need_summary": True, "status": False}
    command = f"cd /home/wac/www/start_script && supervisorctl -c supervisord.conf {action} {task_name}"
    try:
        command = f"ssh wac@{host_ip} '{command}'"
        code, out = subprocess.getstatusoutput(command)  # 运行结束后返回命令行输出，不能边运行边输出
    except:
        return {"msg": "命令执行失败，主机无法连接，请联系管理员检查", "need_summary": True, "status": False}
    logging.info(f"执行命令: {command}, 返回码: {code}, 输出: {out}")
    if code != 0:
        return {"msg": f"操作失败,输出结果是: {out}", "need_summary": True, "status": False}
    else:
        return {"msg": f"操作成功,输出结果是: {out}", "need_summary": True, "status": True}

#######一些utils，依赖函数
def get_graph(host="192.168.50.209", user="neo4j", password="welcome"):
    graph = Graph(
        host=host,
        user=user,
        password=password
    )
    return graph

##### flask 接口

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

class ChatBot(object):
    def __init__(self):
        # 用于根据问题检索原数据，可以被neo4j代替
        self.DocChatUrl = "http://192.168.50.189:8777"
        self.tools = get_tools()
        self.mongo = MongoDBManager()
        self.prompts = self.get_all_prompt()
        self.llm_list = [
            {
                "name": "chatgpt",
                "url": "http://127.0.0.1:4636/api/message",
                "ping": "http://127.0.0.1:4636/ping",
                "model_name": "gpt-3.5-turbo",
                "webapi": False,
                "openai_format": True,
            },
            {
                "name": "qwen7B",
                "url": "http://192.168.50.189:36001/worker_generate_stream",
                "ping": f"http://192.168.50.189:36001/health/ready",
                "webapi": False,
            },
            {
                "name": "MistralAgent",
                "url": "http://192.168.50.209:7066/v1", #base_url:  chat/completions
                "ping": f"http://192.168.50.209:7066/v1/models",
                "model_name": "meetkai/functionary-small-v2.4",
                "webapi": False,
            },
            {
                "name": "Yi34B",
                "url": "http://127.0.0.1:9892/api/message",
                "ping": "http://127.0.0.1:9892/ping",
                "webapi": False,
            },
            {
                "name": "chatgptfree",
                "url": "https://api.chatanywhere.tech/v1/chat/completions",
                "model_name": "gpt-3.5-turbo",
                "webapi": False,
                "openai_format": True,
            },
            {
                "name": "llama3-8B",
                "url": "http://127.0.0.1:4637/api/message",
                "ping": "http://127.0.0.1:4637/ping",
                "model_name": "llama3-8b-8192",
                "webapi": False,
                "openai_format": True,
            },
            {
                "name": "llama3-70B",
                "url": "http://127.0.0.1:4637/api/message",
                "ping": "http://127.0.0.1:4637/ping",
                "model_name": "llama3-70b-8192",
                "webapi": False,
                "openai_format": True,
            },
            {
                "name": "mixtral-8x7b",
                "url": "http://127.0.0.1:4637/api/message",
                "ping": "http://127.0.0.1:4637/ping",
                "model_name": "mixtral-8x7b-32768",
                "webapi": False,
                "openai_format": True,
            },
            # {
            #     "name": "Qwen72B", # 收费的
            #     "url": "http://127.0.0.1:9890/api/message",
            #     "ping": "http://127.0.0.1:9890/ping",
            #     "webapi": False,
            # },
            {
                "name": "glm3-turbo",
                "url": "http://127.0.0.1:9894/api/message",
                "ping": "http://127.0.0.1:9894/ping",
                "model_name": "glm-3-turbo",
                "webapi": False,
            },
            {
                "name": "baichuan",
                "url": "http://192.168.50.189:9898/api/chat",
                "ping": "http://192.168.50.189:9898/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            {
                "name": "doubao",
                "url": "http://192.168.50.189:9893/api/chat",
                "ping": "http://192.168.50.189:9893/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            {
                "name": "kimi",
                "url": "http://192.168.50.189:9895/api/chat",
                "ping": "http://192.168.50.189:9895/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            {
                "name": "zhipu",
                "url": "http://192.168.50.189:9899/api/chat",
                "ping": "http://192.168.50.189:9899/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            {
                "name": "tongyi",
                "url": "http://192.168.50.189:9896/api/chat",
                "ping": "http://192.168.50.189:9896/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            {
                "name": "coze",
                "url": "http://192.168.50.189:9897/api/chat",
                "ping": "http://192.168.50.189:9897/ping",
                "webapi": True,  # 使用网页爬虫做的api
            },
            # {
            #     "name": "mistral",
            #     "url": "http://192.168.50.189:9891/api/chat",
            #     "ping": "http://192.168.50.189:9891/ping",
            #     "webapi": True,  # 使用网页爬虫做的api,不好用，都是英文的
            # },
        ]
        self.export_json = "/Users/admin/git/LLaMA-Factory/data/myself_toolcall.json"
        self.mongo_collections = ["label", "prompt", "question"]
        self.backup_dir = "cache"  # 备份目录
    def start_label_chat(self, messages, prompt="defalut", llm=["chatgpt"], tools="empty", usecache=True):
        """
        开始chat
        Args:
            messages (): [{'id': 1, 'role': 'human', 'content': '你好'}, {'id': 2, 'role': 'gpt', 'content': 'hi,我有什么可以帮助您的？}, {'id': 3, 'role': 'function_call', 'content': '{"name": "query_neo4j", "arguments": {"cql": \'MATCH p=()-[r:BRAND_IS]->(n:Brand {name:"汤姆·福特"}) return p limit 30\'}}'}, {'id': 4, 'role': 'observation', 'content': 'xxxxxx'}, {'id': 5, 'role': 'gpt', 'content': '好的，30个搜索到的产品分别是：xxx,xxx'}]
            prompt (): 可以给prompt的预设名称，或者自己预设prompt, eg: 'sentiment'
            llm (): list
            tools: empty表示不使用工具，all是所有工具，也可以使用部分工具，直接是工具的名称的逗号拼接
        Returns: string
        """
        if tools == "empty":
            tool_names = []
        elif tools == "all":
            tool_names = list(self.tools.keys())
        else:
            tool_names = tools.split(",")
        messages, prompt_template = self.context_and_question_format(messages, prompt)
        response_list = []
        if not tool_names:
            tools = []
            # 如果忘记传工具名称了，那么可以获取到工具名称，根据function_call
            for message in messages:
                if message["role"] == "function_call":
                    one_tool_json = json.loads(message["content"])
                    for one in one_tool_json:
                        tools.append(one["name"])
            tool_names = tools
        for one_llm in llm:
            match_llm_config = [llm for llm in self.llm_list if llm["name"] == one_llm][0]
            is_openai_format = match_llm_config.get("openai_format", False)
            if one_llm == "chatgpt" or is_openai_format:
                url = match_llm_config["url"]
                model_name = match_llm_config["model_name"]
                response_json = self.chatgpt_chat(messages, url, model_name, prompt_template, tool_names, usecache,step_mode=True)
                content = response_json["result"]["content"]
                tool = response_json["result"]["tool_calls"]
                response = {"content": content, "tool_calls": tool}
                response_list.append({
                    "llm": one_llm,
                    "response": response,
                })
            elif one_llm == "MistralAgent":
                response_json = self.functionary_chat(messages, prompt_template, tool_names, usecache, step_mode=True)
                content = response_json["result"]["content"]
                tool = response_json["result"]["tool_calls"]
                response = {"content": content, "tool_calls": tool}
                response_list.append({
                    "llm": one_llm,
                    "response": response,
                })
            elif one_llm == "qwen7B":
                content = self.qwen7B_chat(messages, prompt_template, tool_names)
                response = {"content": content, "tool_calls": []}
                response_list.append({
                    "llm": one_llm,
                    "response": response,
                })
            elif one_llm == "zhipuapi":
                response_json = self.zhipuapi_chat(messages, prompt_template, tool_names, usecache, step_mode=True)
                content = response_json["result"]["content"]
                tool = response_json["result"]["tool_calls"]
                response = {"content": content, "tool_calls": tool}
                response_list.append({
                    "llm": one_llm,
                    "response": response,
                })
            else:
                webapi = [llm for llm in self.llm_list if llm["name"] == one_llm][0]["webapi"]
                if webapi:
                    content = self.webAPI_chat(one_llm, messages, prompt_template, tool_names)
                    response = {"content": content, "tool_calls": []}
                    response_list.append({
                        "llm": one_llm,
                        "response": response,
                    })
                else:
                    response_json = self.otherapi_chat(one_llm, messages, prompt_template, tool_names, usecache)
                    content = response_json["result"]["content"]
                    tool = response_json["result"]["tool_calls"]
                    response = {"content": content, "tool_calls": tool}
                    response_list.append({
                        "llm": one_llm,
                        "response": response,
                    })
        logging.info(f"结束对话，返回结果：{response_list}")
        return response_list
    def start_chat(self, messages, prompt="defalut", llm="chatgpt", tools="empty", usecache=True, verbose=False):
        """
        开始chat
        Args:
            messages (): [{'id': 1, 'role': 'human', 'content': '你好'}, {'id': 2, 'role': 'gpt', 'content': 'hi,我有什么可以帮助您的？}, {'id': 3, 'role': 'function_call', 'content': '{"name": "query_neo4j", "arguments": {"cql": \'MATCH p=()-[r:BRAND_IS]->(n:Brand {name:"汤姆·福特"}) return p limit 30\'}}'}, {'id': 4, 'role': 'observation', 'content': 'xxxxxx'}, {'id': 5, 'role': 'gpt', 'content': '好的，30个搜索到的产品分别是：xxx,xxx'}]
            prompt (): 可以给prompt的预设名称，或者自己预设prompt, eg: 'sentiment'
            llm (): 单个llm进行测试
            tools: empty表示不使用工具，all是所有工具，也可以使用部分工具，直接是工具的名称的逗号拼接
            verbose: 返回相信信息
        Returns: string
        """
        if isinstance(tools, str):
            if tools == "empty":
                tool_names = []
            elif tools == "all":
                tool_names = list(self.tools.keys())
            else:
                tool_names = tools.split(",")
        else:
            tool_names = tools # 列表的格式
        messages, prompt_template = self.context_and_question_format(messages, prompt)
        if not tool_names:
            tools = []
            # 如果忘记传工具名称了，那么可以获取到工具名称，根据function_call
            for message in messages:
                if message["role"] == "function_call":
                    one_tool_json = json.loads(message["content"])
                    for one in one_tool_json:
                        tools.append(one["name"])
            tool_names = tools
        status = True
        match_llm_config = [l for l in self.llm_list if l["name"] == llm][0]
        is_openai_format = match_llm_config.get("openai_format", False)
        if llm == "chatgpt" or is_openai_format:
            url = match_llm_config["url"]
            model_name = match_llm_config["model_name"]
            response_messages = self.chatgpt_chat(messages, url, model_name, prompt_template, tool_names, usecache)
            # 我们只考虑新增的messages，不用以前的, +1是prompt_template的system的prompt
            original_message_length = len(messages) + 1
            response = response_messages[original_message_length:] # 所有新增的messages
        elif llm == "MistralAgent":
            response_messages = self.functionary_chat(messages, prompt_template, tool_names, usecache)
            # 我们只考虑新增的messages，不用以前的, +1是prompt_template的system的prompt
            original_message_length = len(messages) + 1
            response = response_messages[original_message_length:] # 所有新增的messages
        elif llm == "zhipuapi":
            response_messages = self.zhipuapi_chat(messages, prompt_template, tool_names, usecache)
            # 我们只考虑新增的messages，不用以前的, +1是prompt_template的system的prompt
            original_message_length = len(messages) + 1
            response = response_messages[original_message_length:] # 所有新增的messages
        else:
            webapi = [one for one in self.llm_list if one["name"] == llm][0]["webapi"]
            if webapi:
                response = self.webAPI_chat(llm, messages, prompt_template, tool_names)
            else:
                status = False
                response = "不支持的模型，请尝试Chatgpt, Mistral和zhipuapi"
        logging.info(f"结束对话，返回结果：{response}")
        return status, response
    def generate_question_sample(self, prompt, tool_name="", llm=["chatgpt"], usecache=True):
        """
        根据prompt和工具生成问题样例
        Args:
            prompt (): string
            tool_name (): string, or None
        Returns:
        """
        status, msg = True, "success"
        prompt_content = self.get_prompt_by_name(prompt)
        if tool_name:
            tool_description = self.tools[tool_name]["description"]
            prompt_content = prompt_content + "\n" + tool_description
        response_list = []
        for one_llm in llm:
            match_llm_config = [llm for llm in self.llm_list if llm["name"] == one_llm][0]
            is_openai_format = match_llm_config.get("openai_format", False)
            if one_llm == "chatgpt" or is_openai_format:
                url = match_llm_config["url"]
                model_name = match_llm_config["model_name"]
                response_json = self.chatgpt_generate(question=prompt_content, url=url, model_name=model_name, usecache=usecache)
                response = response_json["result"]["content"]
                response_list.append(response)
            elif one_llm == "MistralAgent":
                response_json = self.functionary_generate(question=prompt_content,usecache=usecache)
                response = response_json["result"]["content"]
                response_list.append(response)
            elif one_llm == "qwen7B":
                response = self.qwen7B_generate(question=prompt_content)
                response_list.append(response)
            elif one_llm == "zhipuapi":
                response_json = self.zhipuapi_generate(question=prompt_content, usecache=usecache)
                response = response_json["result"]["content"]
                response_list.append(response)
            else:
                webapi = [llm for llm in self.llm_list if llm["name"] == one_llm][0]["webapi"]
                if webapi:
                    content = self.webAPI_generate(one_llm, prompt_content)
                    response_list.append(content)
                else:
                    response_json = self.otherapi_generate(llm_name=one_llm, question=prompt_content, usecache=usecache)
                    response = response_json["result"]["content"]
                    response_list.append(response)
        resp = "\n".join(response_list)
        return status, msg, resp

    def backup_mongo(self):
        """
        备份mongo数据库
        Returns:
        """
        backup_data = {}
        cnt = 0
        for collection in self.mongo_collections:
            data = self.mongo.read_data(collection=collection)
            for idx, one in enumerate(data):
                _id = one.pop("_id")
                data[idx]["id"] = str(_id)
                gen_time = _id.generation_time
                time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
                data[idx]["time"] = time_str
            cnt += len(data)
            backup_data[collection] = data
        file_name = "backup" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".json"
        export_json_file = os.path.join(self.backup_dir, file_name)
        with open(export_json_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
        print("备份完成,文件路径:", export_json_file)
        return f"{export_json_file},数据条数: {cnt}"

    def get_llm_status(self):
        """
        获取llm的状态
        Returns:
        """
        new_llm_list = []
        for llm in self.llm_list:
            ping_url = llm.get("ping")
            if ping_url:
                try:
                    r = requests.get(ping_url)
                    if r.status_code == 200:
                        llm["status"] = "ok"
                    else:
                        llm["status"] = "error"
                except Exception as e:
                    llm["status"] = "error"
            else:
                llm["status"] = "ok"
            new_llm_list.append(llm)
        return new_llm_list

    def get_prompt_by_name(self, prompt):
        """
        根据prompt名称返回prompt的内容，如果没有找到，返回原来的prompt
        Args:
            prompt ():
        Returns:
        """
        for one in self.prompts:
            if one["name"] == prompt:
                return one["prompt"]
        return prompt

    def get_prompt_name(self, content):
        """
        返回prompt的名称，根据prompt的内容
        Args:
            content (): 可能就是prompt名称，或者pormpt的内容
        Returns:
        """
        for one in self.prompts:
            if one["name"] == content:
                return content
            if one["prompt"] == content:
                return one["name"]
        # 如果发现是default，可能是self.prompts没有更新，那么这时更新下, 下次就没问题了
        self.prompts = self.get_all_prompt()
        return "default"

    def get_prompt_kb(self, prompt):
        """
        根据prompt名称返回知识库名称，如果没有找到，返回None
        Args:
            prompt ():
        Returns:
        """
        for one in self.prompts:
            if one["name"] == prompt:
                return one.get("knowledge_base")
        return None

    def query_knowledgebase(self, question, kbname):
        """
        根据问题找知识库候选段落
        Args:
            question (): string，问题
            kbname: string，知识库名
        Returns:
        """
        def get_one_kbid(kbname):
            url = f"{self.DocChatUrl}/api/local_doc_qa/list_knowledge_base"
            headers = {'content-type': 'application/json'}
            data = {"user_id": "zzp"}
            # 提交form格式数据
            r = requests.post(url, data=json.dumps(data), headers=headers)
            res = r.json()
            data = res["data"]
            assert len(data) > 0, f"还没有创建知识库，所以无法获取知识库的id"
            name2id = {item["kb_name"]: item["kb_id"] for item in data}
            kb_id = name2id.get(kbname)
            assert kb_id is not None, f"知识库{kbname}不存在"
            return kb_id

        kb_id = get_one_kbid(kbname)
        url = f"{self.DocChatUrl}/api/local_doc_qa/local_doc_chat"
        headers = {'content-type': 'application/json'}
        # 使用1个知识库, 其它参数streaming:bool,  history:list
        data = {"user_id": "zzp", "kb_ids": [kb_id], "question": question, "rerank": True}
        # 提交form格式数据
        r = requests.post(url, data=json.dumps(data), headers=headers)
        res = r.json()
        return res

    def context_and_question_format(self, messages, prompt):
        """
        根据prompt决定是否要使用知识库进行检索回答，或者不检索，格式化prompt
        Args:
            messages ():
            prompt ():

        Returns: messages, prompt_template
        """
        prompt_template = self.get_prompt_by_name(prompt)
        prompt_name = self.get_prompt_name(prompt)
        if "{context}" in prompt_template:
            logging.info(f"提示模板中含有context，需要使用使用知识库检索回答")
            # 获取知识库名称
            kbname = self.get_prompt_kb(prompt_name)
            if not kbname:
                logging.error(f"提示模板{prompt_name}中未配置知识库，但是配置了context，请检查")
                return messages, prompt_template
            last_message = messages[-1]
            question = last_message["content"]
            query_meta = self.query_knowledgebase(question, kbname)
            source_documents = query_meta['source_documents']
            context = ";".join(source["content"] for source in source_documents)
            prompt_template = prompt_template.replace("{context}", context)
            prompt_template = prompt_template.replace("{question}", question)
            messages[-1]["content"] = prompt_template
            return messages, None
        elif "{question}" in prompt_template:
            logging.info(f"提示模板中含有question，但是没有context,需要格式化prompt_template后回答")
            last_message = messages[-1]
            question = last_message["content"]
            prompt_template = prompt_template.replace("{question}", question)
            messages[-1]["content"] = prompt_template
            # 不在需要原始的prompt_template了
            return messages, None
        else:
            logging.info(f"提示模板中不含有context和question，直接回答")
            return messages, prompt_template
    def merge_additional_to_messages(self, messages, additional):
        """
        把addtional的信息合并到messages中
        Args:
            messages ():
            additional: eg: {'neo4j': ['烤饼', '饭团', '食物']}
        Returns:
        """
        logging.info(f"开始合并additional信息到messages中, addtional信息: {additional}")
        if additional.get("neo4j"):
            # 存储了neo4j的节点id，那么需要查询节点信息，合并到messages中
            nodes_list = additional.get("neo4j") #
            if nodes_list:
                additional_msg = "选中的节点: " + ",".join(nodes_list) + "\n"
                messages[-1]["content"]= additional_msg + messages[-1]["content"]
        return messages
    def functionary_chat(self, messages, prompt="", tool_names=[], usecache=True, step_mode=False):
        """
        step_chat和chat之间的区别在于step的chat不会一次执行完全工具的调用和处理，而chat遇到函数调用会自动调用完成，返回最终结果
        调用functionary模型进行对话
        测试的对话的角色和openai的一致
        Args:
            messages ():
            prompt ():
            step_mode: bool, 单步模式,
        Returns:
        """
        logging.info(f"开始使用functionary MistralAgent模型进行对话, messages={messages}, prompt={prompt}, tool_names={tool_names}")
        url = [llm for llm in self.llm_list if llm["name"] == "MistralAgent"][0]["url"]
        model_name = [llm for llm in self.llm_list if llm["name"] == "MistralAgent"][0]["model_name"]
        tools = self.format_tools_to_chatgpt(tool_names)
        if tool_names:
            tool_names = tool_names[::-1]  # 反转tool_names，逐个pop tool name
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        last_human_message = ""
        for message in messages:
            role = message["role"]
            if role == "user" or role == "human":
                new_messages.append({"role": "user", "content": message["content"]})
                last_human_message = message["content"]
            elif role == "assistant" or role == "gpt":
                new_messages.append({"role": "assistant", "content": message["content"]})
            elif role == "function_call":
                function_call = json.loads(message["content"])
                if isinstance(function_call, dict):
                    function_calls =[function_call]
                else:
                    function_calls = function_call
                tool_calls = []
                for one_function in function_calls:
                    arguments = one_function["arguments"]
                    if not isinstance(arguments, str):
                        arguments = json.dumps(arguments, ensure_ascii=True)
                        one_tool = {
                            "id": one_function["id"],  # 函数的id，是openai返回的
                            "function": {
                                "name": one_function["name"],
                                "arguments": arguments,
                            },
                            "type": "function",  # 运行类似，默认是函数，还可以是code_interpeter等
                        }
                        tool_calls.append(one_tool)
                    # 这里的content应该是bot思考的内容
                new_messages.append(
                    {"role": "assistant", "content": "", "tool_calls": tool_calls})
            elif role == "tool" or role == "observation":
                new_messages.append({"role": "tool", "content": message["content"], "name": message["name"],
                                     "tool_call_id": message["tool_call_id"]})
        if step_mode:
            result = self.openai_raw_message(new_messages, url, model_name, tools, temperature=0, usecache=usecache,
                                             cache_prefix="functionary.json")
        else:
            result = self.functionary_submit_messages_continues(new_messages, url, model_name, tools,temperature=0,usecache=usecache,cache_prefix="functionary.json")
        return result

    def functionary_submit_messages_continues(self, messages, url, model_name, tools, temperature=0,usecache=True,cache_prefix="functionary.json"):
        """
        一直不间断的调用llm，直到退出, 参考chatlab/chat.py
        Returns:
        """
        data_result = self.openai_raw_message(messages, url, model_name, tools,temperature=temperature,usecache=usecache,cache_prefix=cache_prefix)
        finish_reason = data_result["result"]["finish_reason"]
        function_call = data_result["result"]["function_call"]
        tool_calls = data_result["result"]["tool_calls"]
        content = data_result["result"]["content"]
        last_message_content = messages[-1]["content"]
        last_message_role = messages[-1]["role"]
        if last_message_role == "assistant" and last_message_content == content:
            print(f"助手连续生成了2条一样的回答，陷入了死循环，退出生成，直接返回")
            messages.append({
                'role': 'assistant',
                'content': content,
            })
            return messages
        if finish_reason == "function_call":
            if function_call is None:
                raise ValueError(
                    "Function call was the stated function_call reason without having a complete function call. If you see this, report it as an issue to https://github.com/rgbkrk/chatlab/issues"  # noqa: E501
                )
            logging.info(f"Todo: Function call: {function_call}, 代码还没完成！")
            return messages
        elif finish_reason == "tool_calls":
            if not tool_calls:
                # Todo: 如果生成的结果的原因是tool_calls，但是没有生成tool_calls的函数名称和参数，那么就直接返回,Mistral这个模型的问题
                messages.append({
                    'role': 'assistant',
                    'content': content,
                })
                return messages
            one_message = {
                'role': 'assistant',
                'content': content,
                'tool_calls': [{'type':'function', 'id': call['id'], 'function': {'name': call['name'], 'arguments':call['arguments']}} for call in tool_calls]
            }
            messages.append(one_message)
            for tool_info in tool_calls:
                #调用函数，结果加到messages
                result = dispatch_tool(tool_info["name"], tool_info["arguments"])
                run_msg = result['msg']
                if isinstance(run_msg,dict) or isinstance(run_msg, list):
                    run_msg = json.dumps(run_msg, ensure_ascii=False)
                assert isinstance(run_msg, str), f"函数的输出结果必须转换成字符串才行,现在不是，请检查: {run_msg}"
                #结果function_called_result加到message
                one_message = {
                    'role': 'tool',
                    'name': tool_info["name"],
                    'content': run_msg,
                    'tool_call_id':  tool_info["id"],
                    'status': result["status"], # 工具运行的状态
                    'meta': result["meta"],
                    'need_summary': result["need_summary"],
                }
                messages.append(one_message)
            return self.functionary_submit_messages_continues(messages, url, model_name, tools,temperature=temperature,usecache=usecache,cache_prefix=cache_prefix)
        # 其它原因导致的chat退出
        elif finish_reason == "stop":
            messages.append({
                'role': 'assistant',
                'content': content,
            })
            return messages
        elif finish_reason == "max_tokens" or finish_reason == "length":
            print("max tokens or overall length is too high...\n")
        elif finish_reason == "content_filter":
            print("Content omitted due to OpenAI content filters...\n")
        else:
            print(
                f"UNKNOWN FINISH REASON: '{finish_reason}'. If you see this message, report it as an issue to https://github.com/rgbkrk/chatlab/issues"  # noqa: E501
            )
    def functionary_generate(self, question, prompt="", usecache=True):
        """
        单个prompt和问题，可以没有prompt
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用functionary模型生成, 问题是：{question}\n prompt是: {prompt}")
        url = [llm for llm in self.llm_list if llm["name"] == "functionary"][0]["url"]
        model_name = [llm for llm in self.llm_list if llm["name"] == "functionary"][0]["model_name"]
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        new_messages.append({"role": "user", "content": question})
        result = self.openai_raw_message(new_messages, url, model_name, tools=None,temperature=0.5,usecache=usecache,cache_prefix="functionary.json")
        return result

    def openai_raw_message(self, messages, base_url, model_name, tools=None, temperature=0.5, usecache=True, cache_prefix="openai.json"):
        """
        直接给openai发送组装好的messages信息
        :param data: 输入的数据
        :param time_sleep: 每次调用的间隔
        """
        client = OpenAI(base_url=base_url, api_key="functionary")
        logging.info(f"输入的数据的messages: {messages}")
        md5 = cal_md5(messages)
        cache_result = load_cache(md5, prefix=cache_prefix)
        if cache_result and usecache:
            logging.info(f"有缓存结果，不用预测了")
            return cache_result
        if tools:
            completions = client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=temperature,
                tools=tools,
                tool_choice="auto",
                stream=False
            )
        else:
            completions = client.chat.completions.create(
                messages=messages,
                model=model_name,
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
        cache_predict(data=one_data, md5=md5, prefix=cache_prefix)
        return one_data

    def qwen7B_chat(self, messages, prompt_template="", tool_names=[]):
        """
        使用DocChat的qwen7B模型进行对话
        Args:
            messages ():
            prompt_template ():
            tool_names ():
        Returns:
        """
        logging.info(
            f"开始使用qwen7B模型进行对话, 输入的messages是：{messages}, prompt_template是：{prompt_template}, tool_names是：{tool_names}")
        url = [llm for llm in self.llm_list if llm["name"] == "qwen7B"][0]["url"]
        headers = {'content-type': 'application/json'}
        # 直接进行LLM问答, Qwen， 这些作为prompt的提示
        tools = self.format_tools_to_chatgpt(tool_names, to_json=True)
        if tools:
            prompt_template = prompt_template + "可用工具:" + ";".join(tools)
        hist_messages = {}
        if prompt_template:
            hist_messages["system"] = {"user": prompt_template, "chatbot": "OK"}
        # 最后一条message作为问题
        last_message = messages.pop()
        last_question = last_message["content"]
        # 其它messages作为历史记录添加
        user_content = ""
        chatbot_content = ""
        for idx, message in enumerate(messages):
            if message["role"] == "human":
                if user_content and chatbot_content:
                    hist_messages[f"user_{idx}"] = {"user": user_content, "chatbot": chatbot_content}
                    user_content = ""
                    chatbot_content = ""
                user_content += message["content"]
            elif message["role"] == "function_call":
                user_content += "使用的工具的参数" + message["content"]
            elif message["role"] == "observation":
                user_content += "工具调用的观察结果" + message["content"]
            elif message["role"] == "gpt":
                chatbot_content += message["content"]
        if user_content and chatbot_content:
            hist_messages[f"user_{idx + 1}"] = {"user": user_content, "chatbot": chatbot_content}
        data = {
            'model': 'yd_gpt',
            'prompt': last_question,
            'hist_messages': hist_messages,
            'temperature': 0.6,
            'max_new_tokens': 300,
            'top_p': 1.0,
            'top_k': 4,
            'repetition_penalty': 1.2,
            'check_in': 0,
            'random_seed': 100,
            'stop': None
        }
        # 提交form格式数据
        logging.info(f"qwen7B的请求参数是：{data}")
        r = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
        words = ""
        for chunk_byte in r.iter_content(chunk_size=1024):
            chunk_string = chunk_byte.decode('utf-8', errors="ignore")
            json_data = chunk_string.replace('data: ', '').replace('\n', '')
            data = json.loads(json_data)
            text_content = data["text"]
            words += text_content
        return words

    def qwen7B_generate(self, question, prompt=""):
        """
        生成，不是问答，类似chatgpt_generate
        Args:
        Returns:
        """
        logging.info(f"开始使用qwen7B模型进行对话, 问题：{question}, 提示：{prompt}")
        url = [llm for llm in self.llm_list if llm["name"] == "qwen7B"][0]["url"]
        headers = {'content-type': 'application/json'}
        # 直接进行LLM问答, Qwen， 这些作为prompt的提示
        if prompt:
            hist_messages = {"system": {"user": prompt, "chatbot": "OK"}}
        else:
            hist_messages = {}
        data = {
            'model': 'yd_gpt',
            'prompt': question,
            'hist_messages': hist_messages,
            'temperature': 0.6,
            'max_new_tokens': 300,
            'top_p': 1.0,
            'top_k': 4,
            'repetition_penalty': 1.2,
            'check_in': 0,
            'random_seed': 100,
            'stop': None
        }
        # 提交form格式数据
        logging.info(f"qwen7B的请求参数是：{data}")
        r = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
        words = ""
        for chunk_byte in r.iter_content(chunk_size=1024):
            chunk_string = chunk_byte.decode('utf-8', errors="ignore")
            json_data = chunk_string.replace('data: ', '').replace('\n', '')
            data = json.loads(json_data)
            text_content = data["text"]
            words += text_content
        return words

    def webAPI_chat(self, llm_name, messages, prompt_template="", tool_names=[]):
        """
        网页做的api
        Args:
            messages ():
            prompt_template ():
            tool_names ():
        Returns:
        """
        logging.info(
            f"开始使用{llm_name}模型进行对话, 输入的messages是：{messages}, prompt_template是：{prompt_template}, tool_names是：{tool_names}")
        url = [llm for llm in self.llm_list if llm["name"] == llm_name][0]["url"]
        headers = {'content-type': 'application/json'}
        # 直接进行LLM问答, Qwen， 这些作为prompt的提示
        tools = self.format_tools_to_chatgpt(tool_names, to_json=True)
        if tools:
            prompt_template = prompt_template + "可用工具:" + ";".join(tools)
        # 最后一条message作为问题
        last_message = messages.pop()
        last_question = last_message["content"]
        # 其它messages作为历史记录添加, 网页做的api不用传历史对话信息，网页上有历史对话信息了
        # history = json.dumps(messages,ensure_ascii=False)
        # question = prompt_template + "\n历史对话信息:" + history + "\n" + last_question
        data = {
            'question': last_question,
        }
        logging.info(f"{llm_name}的请求参数是：{data}")
        r = requests.post(url, data=json.dumps(data), headers=headers)
        res = r.json()
        logging.info(f"{llm_name}的回答是：{res}")
        answer = res["answer"]
        return answer

    def webAPI_generate(self, llm_name, question, prompt=""):
        """
        网页做的API，chat
        Args:
        Returns:
        """
        logging.info(f"开始使用{llm_name}模型进行对话, 问题：{question}, 提示：{prompt}")
        url = [llm for llm in self.llm_list if llm["name"] == llm_name][0]["url"]
        headers = {'content-type': 'application/json'}
        # 直接进行LLM问答,这些作为prompt的提示
        if prompt:
            question += prompt + "\n" + question
        data = {
            'question': question,
        }
        # 提交form格式数据
        logging.info(f"{llm_name}的请求参数是：{data}")
        r = requests.post(url, data=json.dumps(data), headers=headers)
        res = r.json()
        answer = res["answer"]
        return answer

    def format_tools_to_chatgpt(self, tool_names, to_json=False):
        """
        格式化工具为chatgpt的格式
        Args:
            tool_names (): list

        Returns:
        """
        tools = []
        for tool_name in tool_names:
            tool_description = self.tools[tool_name]
            params = tool_description["params"]
            required = []
            properties = {}
            for param in params:
                param_name = param["name"]
                if param["required"]:
                    required.append(param_name)
                properties[param_name] = {
                    "type": param["type"],
                    "description": param["description"],
                }
            base_template = {
                "type": "function",
                "function": {
                    "name": tool_description["name"],
                    "description": tool_description["description"],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            }
            if to_json:
                base_template = json.dumps(base_template, ensure_ascii=False)
            tools.append(base_template)
        return tools

    def chatgpt_chat(self, messages, url, model_name, prompt="", tool_names=[], usecache=True, step_mode=False):
        """
        调用chatgpt接口
        Args:
            messages ():
            prompt ():
            step_mode: 是否逐步运行还是一次运行
        Returns:
        """
        logging.info(f"开始使用{model_name}模型进行对话, messages={messages}, prompt={prompt}, tool_names={tool_names}")
        tools = self.format_tools_to_chatgpt(tool_names)
        if tool_names:
            tool_names = tool_names[::-1]  # 反转tool_names，逐个pop tool name
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        last_human_message = ""
        for message in messages:
            role = message["role"]
            if role == "user" or role == "human":
                new_messages.append({"role": "user", "content": message["content"]})
                last_human_message = message["content"]
            elif role == "assistant" or role == "gpt":
                new_messages.append({"role": "assistant", "content": message["content"]})
            elif role == "function_call":
                function_call = json.loads(message["content"])
                if isinstance(function_call, dict):
                    function_calls =[function_call]
                else:
                    function_calls = function_call
                tool_calls = []
                for one_function in function_calls:
                    arguments = one_function["arguments"]
                    if not isinstance(arguments, str):
                        arguments = json.dumps(arguments)
                    one_tool = {
                        "id": one_function["id"], # 函数的id，是openai返回的
                        "function": {
                            "name": one_function["name"],
                            "arguments": arguments,
                        },
                        "type": "function", # 运行类似，默认是函数，还可以是code_interpeter等
                    }
                    tool_calls.append(one_tool)
                # 这里的content应该是bot思考的内容
                new_messages.append(
                    {"role": "assistant", "content": "", "tool_calls": tool_calls})
            elif role == "tool" or role == "observation":
                new_messages.append({"role": "tool", "content": message["content"], "name": message["name"],"tool_call_id":message["tool_call_id"]})
        if step_mode:
            params = {'message': new_messages, "temperature": 0, "usecache": usecache, "model_name":model_name}
            if tool_names:
                params["tools"] = tools
            headers = {'content-type': 'application/json'}
            logging.info(f"{model_name}的请求参数是：{params}")
            r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
            result = r.json()
        else:
            result = self.chatgpt_submit_messages_continues(new_messages,url,tools,temperature=0,usecache=usecache,model_name=model_name)
        return result
    def chatgpt_submit_messages_continues(self, messages, url, tools, temperature=0,usecache=True,model_name="gpt-3.5-turbo"):
        """
        一直不间断的调用llm，直到退出, 参考chatlab/chat.py
        Returns:
        """
        def post_request():
            params = {'message': messages, "temperature": 0, "usecache": usecache, "tools":tools, "model_name":model_name}
            headers = {'content-type': 'application/json'}
            logging.info(f"Chatgpt或者Zhipu的请求参数是：{params}")
            r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
            result = r.json()
            return result
        data_result = post_request()
        finish_reason = data_result["result"]["finish_reason"]
        function_call = data_result["result"]["function_call"]
        tool_calls = data_result["result"]["tool_calls"]
        content = data_result["result"]["content"]
        last_message_content = messages[-1]["content"]
        last_message_role = messages[-1]["role"]
        if last_message_role == "assistant" and last_message_content == content:
            print(f"助手连续生成了2条一样的回答，陷入了死循环，退出生成，直接返回")
            messages.append({
                'role': 'assistant',
                'content': content,
            })
            return messages
        if finish_reason == "function_call":
            if function_call is None:
                raise ValueError(
                    "Function call was the stated function_call reason without having a complete function call. If you see this, report it as an issue to https://github.com/rgbkrk/chatlab/issues"  # noqa: E501
                )
            logging.info(f"Todo: Function call: {function_call}, 代码还没完成！")
            return messages
        elif finish_reason == "tool_calls":
            if not tool_calls:
                # Todo: 如果生成的结果的原因是tool_calls，但是没有生成tool_calls的函数名称和参数，那么就直接返回
                messages.append({
                    'role': 'assistant',
                    'content': content,
                })
                return messages
            one_message = {
                'role': 'assistant',
                'content': content,
                'tool_calls': [{'type':'function', 'id': call['id'], 'function': {'name': call['name'], 'arguments':call['arguments']}} for call in tool_calls]
            }
            messages.append(one_message)
            for tool_info in tool_calls:
                #调用函数，结果加到messages
                result = dispatch_tool(tool_info["name"], tool_info["arguments"])
                run_msg = result['msg']
                if isinstance(run_msg,dict) or isinstance(run_msg, list):
                    run_msg = json.dumps(run_msg, ensure_ascii=False)
                assert isinstance(run_msg, str), f"函数的输出结果必须转换成字符串才行,现在不是，请检查: {run_msg}"
                #结果function_called_result加到message
                one_message = {
                    'role': 'tool',
                    'name': tool_info["name"],
                    'content': run_msg,
                    'tool_call_id':  tool_info["id"]
                }
                messages.append(one_message)
            return self.chatgpt_submit_messages_continues(messages,url,tools,temperature=temperature,usecache=usecache,model_name=model_name)
        # 其它原因导致的chat退出
        elif finish_reason == "stop":
            messages.append({
                'role': 'assistant',
                'content': content,
            })
            return messages
        elif finish_reason == "max_tokens" or finish_reason == "length":
            print("max tokens or overall length is too high...\n")
        elif finish_reason == "content_filter":
            print("Content omitted due to OpenAI content filters...\n")
        else:
            print(
                f"UNKNOWN FINISH REASON: '{finish_reason}'. If you see this message, report it as an issue to https://github.com/rgbkrk/chatlab/issues"  # noqa: E501
            )
    def chatgpt_generate(self, question, url, model_name, prompt="", usecache=True):
        """
        单个prompt和问题，可以没有prompt
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用{model_name}模型生成, 问题是：{question}\n prompt是: {prompt}")
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        new_messages.append({"role": "user", "content": question})
        params = {'message': new_messages, "temperature": 0.5, "usecache": usecache, "model_name":model_name}
        headers = {'content-type': 'application/json'}
        logging.info(f"{model_name}的请求参数是：{params}")
        r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
        result = r.json()
        return result

    def otherapi_chat(self, llm_name, messages, prompt="", tool_names=[], usecache=True):
        """
        其它形式的api
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用{llm_name}模型进行对话, messages={messages}, prompt={prompt}, tool_names={tool_names}")
        url = [llm for llm in self.llm_list if llm["name"] == llm_name][0]["url"]
        tools = self.format_tools_to_chatgpt(tool_names)
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        for message in messages:
            role = message["role"]
            if role == "human":
                new_messages.append({"role": "user", "content": message["content"]})
            elif role == "gpt":
                new_messages.append({"role": "assistant", "content": message["content"]})
            elif role == "observation":
                new_messages.append({"role": "user", "content": "可供参考信息:" + message["content"]})
        params = {'message': new_messages, "temperature": 0.5, "usecache": usecache}
        if tool_names:
            params["tools"] = tools
        headers = {'content-type': 'application/json'}
        logging.info(f"{llm_name}的请求参数是：{params}")
        r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
        result = r.json()
        return result

    def otherapi_generate(self, llm_name, question, prompt="", usecache=True):
        """
        其它形式的api
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用{llm_name}模型生成, 问题是：{question}， prompt是: {prompt}")
        url = [llm for llm in self.llm_list if llm["name"] == llm_name][0]["url"]
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        new_messages.append({"role": "user", "content": question})
        params = {'message': new_messages, "temperature": 0.5, "usecache": usecache}
        headers = {'content-type': 'application/json'}
        logging.info(f"{llm_name}的请求参数是：{params}")
        r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
        result = r.json()
        return result

    def zhipuapi_chat(self, messages, prompt="", tool_names=[], usecache=True, step_mode=False):
        """
        调用zhipuapi的chat接口, https://maas.aminer.cn/dev/api#glm-3-turbo
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用zhipuapi模型进行对话, messages={messages}, prompt={prompt}, tool_names={tool_names}")
        url = [llm for llm in self.llm_list if llm["name"] == "zhipuapi"][0]["url"]
        model_name = [llm for llm in self.llm_list if llm["name"] == "zhipuapi"][0]["model_name"]
        tools = self.format_tools_to_chatgpt(tool_names)
        if tool_names:
            tool_names = tool_names[::-1]  # 反转tool_names，逐个pop tool name
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        last_human_message = ""
        for message in messages:
            role = message["role"]
            if role == "user" or role == "human":
                new_messages.append({"role": "user", "content": message["content"]})
                last_human_message = message["content"]
            elif role == "assistant" or role == "gpt":
                new_messages.append({"role": "assistant", "content": message["content"]})
            elif role == "function_call":
                function_call = json.loads(message["content"])
                if isinstance(function_call, dict):
                    function_calls =[function_call]
                else:
                    function_calls = function_call
                tool_calls = []
                for one_function in function_calls:
                    arguments = one_function["arguments"]
                    if not isinstance(arguments, str):
                        arguments = json.dumps(arguments)
                    one_tool = {
                        "id": one_function["id"], # 函数的id，是openai返回的
                        "function": {
                            "name": one_function["name"],
                            "arguments": arguments,
                        },
                        "type": "function", # 运行类似，默认是函数，还可以是code_interpeter等
                    }
                    tool_calls.append(one_tool)
                # 这里的content应该是bot思考的内容
                new_messages.append(
                    {"role": "assistant", "content": "", "tool_calls": tool_calls})
            elif role == "tool" or role == "observation":
                new_messages.append({"role": "tool", "content": message["content"], "name": message["name"],"tool_call_id":message["tool_call_id"]})
        if step_mode:
            params = {'message': new_messages, "temperature": 0, "usecache": usecache}
            if tool_names:
                params["tools"] = tools
            headers = {'content-type': 'application/json'}
            logging.info(f"zhipuAPI的请求参数是：{params}")
            r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
            result = r.json()
        else:
            result = self.chatgpt_submit_messages_continues(new_messages,url,tools,temperature=0,usecache=usecache,model_name=model_name)
        return result

    def zhipuapi_generate(self, question, prompt="", usecache=True):
        """
        单个prompt和问题，可以没有prompt
        Args:
            messages ():
            prompt ():
        Returns:
        """
        logging.info(f"开始使用zhipuapi模型生成, 问题是：{question}， prompt是: {prompt}")
        url = [llm for llm in self.llm_list if llm["name"] == "zhipuapi"][0]["url"]
        # 把前端传过来的messages换成openai的格式
        new_messages = []
        if prompt:
            new_messages.append({"role": "system", "content": prompt})
        new_messages.append({"role": "user", "content": question})
        params = {'message': new_messages, "temperature": 0.5, "usecache": usecache}
        headers = {'content-type': 'application/json'}
        logging.info(f"zhipuAPI的请求参数是：{params}")
        r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
        result = r.json()
        return result

    def save_messages(self, messages, prompt, tools,id=None,collection="label"):
        """
        保存messages到mongo数据库
        Args:
            messages ():
            prompt ():
            tools ():
            id: 如果给了mongo的id，那么就更新数据
            collection (): 默认保存到label中，表示人工检查过的数据，还可以保存到llmlabel中，表示llm标注的数据，未经过人工检查， wronglabel 表示存储错误的回答情况的数据
        Returns:
        """
        if collection not in ["label", "llmlabel", "wronglabel"]:
            return False, "collection参数错误,只能是label, llmlabel, wronglabel这几个表"
        # 检查messages，查看使用的tools有哪些
        status, msg = self.valid_messages(messages)
        if not status:
            return False, msg
        prompt_content = self.get_prompt_by_name(prompt)
        prompt_name = self.get_prompt_name(prompt)
        # 工具有可能也不是用的本地的工具，有可能是其它的工具
        if tools is None or not tools or None in tools:
            tools = []
            for message in messages:
                if message["role"] == "observation":
                    if message.get("name"):
                        tools.append(message["name"])
        tools_info = [self.tools[tool] for tool in tools]
        if id:
            # 更新数据
            one_data = {
                "$set": {
                    "messages": messages,
                    "prompt": prompt_content,
                    "prompt_name": prompt_name,
                    "tools": tools_info,
                }
            }
            try:
                status, msg = self.mongo.update_one_data(query={"id": id}, new_values=one_data, collection=collection)
                return status, msg
            except Exception as e:
                logging.error(f"修改数据失败: {e}")
                return False, f"修改数据失败: {e}"
        else:
            # 插入一条数据
            one_data = {
                "messages": messages,
                "prompt": prompt_content,
                "prompt_name": prompt_name,
                "tools": tools_info,
            }
            try:
                self.mongo.insert_data(data=[one_data], collection=collection)
                return True, "插入数据成功"
            except Exception as e:
                logging.error(f"插入数据失败: {e}")
                return False, f"插入数据失败: {e}"

    def update_message(self, id, messages, prompt_name, prompt, tools):
        # 修改message后更新保存内容
        status, msg = self.valid_messages(messages)
        if not status:
            return False, msg
        prompt_content = self.get_prompt_by_name(prompt)
        tools_info = [self.tools[tool] for tool in tools]
        # 更新一条数据
        one_data = {
            "$set": {
                "messages": messages,
                "prompt": prompt_content,
                "prompt_name": prompt_name,
                "tools": tools_info,
            }
        }
        try:
            status, msg = self.mongo.update_one_data(query={"_id": id}, new_values=one_data, collection='label')
            return status, msg
        except Exception as e:
            logging.error(f"插入数据失败: {e}")
            return False, f"插入数据失败: {e}"

    def valid_messages(self, messages):
        """
        验证messages是否合法,如果合法，那么返回True，否则返回False
        Args:
            messages ():
        Returns:
        """
        orders = {
            "human": ["gpt", "function_call"],  # 验证hunam的下一个是gpt
            "gpt": ["human"],  # 验证gpt的下一个是human或者function_call
            "function_call": ["observation"],  # 验证function_call的下一个是observation
            "observation": ["gpt","observation","thought"],  # 验证observation的下一个是gpt或者observation
            "user":["assistant","SOP"], # User后面的角色
            "SOP": ["assistant", "thought"], # 标注工作流workflow后面的角色
            "thought": ["observation","assistant"],  #  思考后面的角色可能是观察或者assistant
        }
        last_role = messages[-1]["role"]
        if last_role not in ["gpt","assistant"] :
            logging.warning(f"检查messages失败: 最后的回答不是gpt或者assistant回答的")
            return False, "最后的回答一定是gpt回答的或者assistant，目前不是"
        for idx, message in enumerate(messages):
            content = message.get("content")
            if not content:
                logging.warning(f"检查messages失败: 内容为空")
                return False, "内容不能为空"
            role = message["role"]
            if idx == len(messages) - 1:
                # 没有下一个message了，可以跳过了
                continue
            next_role = messages[idx + 1]["role"]
            next_should_be = orders[role]
            if next_role not in next_should_be:
                logging.warning(f"检查messages失败: 第{idx + 1}个回答的下一个回答应该是{next_should_be},但是现在是{next_role}")
                return False, f"第{idx + 1}个回答的下一个回答应该是{next_should_be},但是现在是{next_role}"
        # 检查每个messages的函数中的函数名称是否在函数列表中
        for idx, message in enumerate(messages):
            if message["role"] == "function_call":
                content = message["content"]
                # 加载成json格式
                try:
                    content_json = json.loads(content)
                except json.JSONDecodeError:
                    logging.warning(f"检查messages失败: 第{idx + 1}个回答的函数内容不是json格式")
                    return False, f"第{idx + 1}个回答的函数内容不是json格式"
                for func_idx, one_json in enumerate(content_json):
                    function_name = one_json["name"]
                    if function_name not in self.tools:
                        logging.warning(f"检查messages失败: 第{idx + 1}个回答的第{func_idx}个函数名{function_name}不在工具列表中")
                        return False, f"第{idx + 1}个回答的第{func_idx}个函数名{function_name}不在工具列表中"
        logging.info(f"检查messages成功")
        return True, "验证通过"

    def query_messages(self,keyword,field="all", mode="detail", limit=-1):
        """
        获取所有数据
        Args:
            mode (): detail 表示详细结果, sample表示简单结果
            limit: 200, 默认获取200条数据，如果为-1，表示获取所有数据
        Returns:
        """
        data = self.mongo.read_data(collection='label', number=limit)
        # id变成字符串，格式的
        for idx, one in enumerate(data):
            _id = one.pop("_id")
            data[idx]["id"] = str(_id)
            gen_time = _id.generation_time
            # 创建一个代表UTC+8的时区
            tz_utc_8 = datetime.timezone(timedelta(hours=8))
            # 将当前时间转换为UTC+8时区（北京时间）
            gen_time = gen_time.astimezone(tz_utc_8)
            time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
            data[idx]["time"] = time_str
        if mode == "sample":
            # 对数据再次进行简化
            new_data = []
            for idx, one in enumerate(data):
                messages = one["messages"]
                message = ""
                for m in messages:
                    message += m.get("role","") + ":" + m.get("content","") + "\n"
                data[idx]["messages_concat"] = message
                tools = one["tools"]
                tools = ";".join(t["name"] for t in tools)
                data[idx]["tools_concat"] = tools
                prompt_name = one["prompt_name"]
                prompt = one["prompt"]
                if field == "all" and (keyword in prompt_name or keyword in prompt or keyword in tools or keyword in message):
                    new_data.append(one)
                elif field == "prompt" and keyword in prompt:
                    new_data.append(one)
                elif field == "tools" and keyword in tools:
                    new_data.append(one)
                elif field == "message" and keyword in message:
                    new_data.append(one)
                elif field == "prompt_name" and keyword in prompt_name:
                    new_data.append(one)
            data = new_data
        else:
            # 对数据按照field要求过滤
            new_data = []
            for idx, one in enumerate(data):
                messages = one["messages"]
                all_content = ""
                for m in messages:
                    all_content += m.get("role","") + ":" + m.get("content","") + "\n"
                tools = one["tools"]
                prompt_name = one["prompt_name"]
                prompt = one["prompt"]
                if field == "all" and (keyword in prompt_name or keyword in prompt or keyword in tools or keyword in all_content):
                    new_data.append(one)
                elif field == "prompt" and keyword in prompt:
                    new_data.append(one)
                elif field == "tools" and keyword in tools:
                    new_data.append(one)
                elif field == "message" and keyword in all_content:
                    new_data.append(one)
                elif field == "prompt_name" and keyword in prompt_name:
                    new_data.append(one)
            data = new_data
        return data
    def get_all_messages(self, mode="detail", limit=-1, prompt="all"):
        """
        获取所有数据
        Args:
            mode (): detail 表示详细结果, sample表示简单结果
            limit: 200, 默认获取200条数据，如果为-1，表示获取所有数据
            prompt: 根据prompt进行过滤
        Returns:
        """
        data = self.mongo.read_data(collection='label', number=limit)
        if prompt != "all":
            # 过滤下数据
            data = [i for i in data if i["prompt_name"] == prompt]
        # id变成字符串，格式的
        for idx, one in enumerate(data):
            _id = one.pop("_id")
            data[idx]["id"] = str(_id)
            gen_time = _id.generation_time
            # 创建一个代表UTC+8的时区
            tz_utc_8 = datetime.timezone(timedelta(hours=8))
            # 将当前时间转换为UTC+8时区（北京时间）
            gen_time = gen_time.astimezone(tz_utc_8)
            time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
            data[idx]["time"] = time_str
        if mode == "sample":
            # 对数据再次进行简化
            for idx, one in enumerate(data):
                messages = one["messages"]
                message = ""
                for m in messages:
                    message += m.get("role","") + ":" + m.get("content","") + "\n"
                data[idx]["messages_concat"] = message
                tools = one["tools"]
                tools = ";".join(t["name"] for t in tools)
                data[idx]["tools_concat"] = tools
        return data
    def get_total_messages_number(self):
        """
        获取message的总条数
        Returns: int
        """
        number = self.mongo.read_data_count()
        return number
    def delete_message(self, id):
        """
        根据数据的id，删除1条message
        Args:
            name ():
        Returns:
        """
        try:
            status, msg = self.mongo.delete_one_data(query={"_id": id}, collection='label')
            return status, msg
        except Exception as e:
            logging.error(f"删除数据失败: {e}")
            return False, f"删除数据失败: {e}"

    def clear_mongo_db(self):
        # 清空数据库
        self.mongo.insert_data(only_clean=True)

    def export_all_data(self):
        """
        导出数据到json文件,导出到 self.export_json
        Returns:
        """
        data = self.get_all_messages()
        export_data = []
        for one in data:
            tool_info = one.pop("tools")
            tool_names = [t["name"] for t in tool_info]
            messages = one.pop("messages")
            prompt = one.pop("prompt")
            tools_all = self.format_tools_to_chatgpt(tool_names)
            tools = [f["function"] for f in tools_all]
            # prompt作为系统的提示
            conversations = [{"from": "system", "value": prompt}]
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                conversations.append({"from": role, "value": content})
            export_data.append({"conversations": conversations, "tools": json.dumps(tools, ensure_ascii=False)})
        with open(self.export_json, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
        logging.info(f"导出数据到{self.export_json},导出了{len(export_data)}条数据")
        return self.export_json

    def add_prompt(self, name, prompt, usage, knowledge_base=""):
        """
        添加1条prompt
        prompt: string，内容
        usage: string，使用场景, QA, generate等
        Returns:
        """
        if knowledge_base:
            if "{context}" not in prompt and "{question}" not in prompt:
                return False, "注意，如果给定知识库，那么prompt里面必须包含{context}和{question}两个变量，请修改prompt"
        one_data = {
            "name": name,
            "prompt": prompt,
            "usage": usage,
            "knowledge_base": knowledge_base,
        }
        try:
            self.mongo.insert_data(data=[one_data], collection='prompt')
            # 更新下prompt
            self.prompts = self.get_all_prompt()
            return True, "插入数据成功"
        except Exception as e:
            logging.error(f"插入数据失败: {e}")
            return False, "插入数据失败"

    def modify_prompt(self, name, prompt, usage, knowledge_base=""):
        """
        修改prompt
        prompt: string，内容
        usage: string，使用场景, QA, generate等
        Returns:
        """
        if knowledge_base:
            if "{context}" not in prompt or "{question}" not in prompt:
                return False, "注意，如果给定知识库，那么prompt里面必须包含{context}和{question}两个变量，请修改prompt"
        one_data = {
            "$set": {
                "name": name,
                "prompt": prompt,
                "usage": usage,
                "knowledge_base": knowledge_base,
            }
        }
        try:
            status, msg = self.mongo.update_one_data(query={"name": name}, new_values=one_data, collection='prompt')
            # 更新下prompt
            self.prompts = self.get_all_prompt()
            return status, msg
        except Exception as e:
            logging.error(f"修改数据失败: {e}")
            return False, f"修改数据失败: {e}"

    def get_all_prompt(self):
        """
        获取所有prompt
        {
            "name" : "gen_tool_question",
            "prompt" : "请根据下面的工具的说明，生成50个用户可能问的问题，可以使用该工具结果进行回答， 生成的每个问题用换行隔开，直接生成问题即可。工具是：",
            "usage" : "根据提供的工具生成一些问题"
        }
        Args:
        Returns:
        """
        data = self.mongo.read_data(collection='prompt')
        # id变成字符串，格式的
        for idx, one in enumerate(data):
            _id = one.pop("_id")
            data[idx]["id"] = str(_id)
            gen_time = _id.generation_time
            # 创建一个代表UTC+8的时区
            tz_utc_8 = datetime.timezone(timedelta(hours=8))
            # 将当前时间转换为UTC+8时区（北京时间）
            gen_time = gen_time.astimezone(tz_utc_8)
            time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
            data[idx]["time"] = time_str
        return data
    def get_all_prompt_questions(self):
        """
        获取所有prompt和prompt生成的问题指令集
        {
            "name" : "gen_tool_question",
            "prompt" : "请根据下面的工具的说明，生成50个用户可能问的问题，可以使用该工具结果进行回答， 生成的每个问题用换行隔开，直接生成问题即可。工具是：",
            "usage" : "根据提供的工具生成一些问题"
            "questions": [],
            "question_content": str,
            "llm": "chatgpt"
        }
        Args:
        Returns:
        """
        prompts = self.get_all_prompt()
        questions = self.get_all_questions()
        question_prompt_dict = {one["prompt"]:one for one in questions}
        for idx, one_prompt in enumerate(prompts):
            prompt = one_prompt["prompt"]
            name = one_prompt["name"]
            # 分别尝试promt的内容和名称去匹配问题库
            question = question_prompt_dict.get(prompt)
            if not question:
                question = question_prompt_dict.get(name)
            if question:
                one_prompt["questions"] = question["questions"]
                one_prompt["number"] = question["number"]
                one_prompt["question_content"] = question["question_content"]
                one_prompt["question_id"] = question["id"]
                one_prompt["llm"] = question["llm"]
            else:
                one_prompt["questions"] = []
                one_prompt["number"] = 0
                one_prompt["question_content"] = ""
            prompts[idx] = one_prompt
        return prompts

    def delete_prompt(self, name):
        """
        按名称删除1条prompt
        Args:
            name ():
        Returns:
        """
        if name in ["default", "gen_tool_question"]:
            return False, "这个prompt只能修改，不能被删除"
        try:
            status, msg = self.mongo.delete_one_data(query={"name": name}, collection='prompt')
            # 更新下prompt
            self.prompts = self.get_all_prompt()
            return True, msg
        except Exception as e:
            logging.error(f"删除数据失败: {e}")
            return False, f"删除数据失败: {e}"

    def modify_question(self, prompt, question_content, llm):
        """
        更新question
        prompt: string，根据prompt判断是否存在，如果存在，那么就进行更新
        Returns:
        """
        try:
            questions = []
            for one in question_content.split("\n"):
                one = one.strip()
                question = re.sub(r"\d+\.\s*", "", one)
                questions.append(question)
        except Exception as e:
            return False, f"数据无法按行进行处理,{e}"
        one_data = {
            "$set": {
                "llm": llm,
                "prompt": prompt,
                "question_content": question_content,
                "questions": questions,
            }
        }
        try:
            status, msg = self.mongo.update_one_data(query={"prompt": prompt}, new_values=one_data,
                                                     collection='question')
            # 更新下prompt
            return status, msg
        except Exception as e:
            logging.error(f"修改数据失败: {e}")
            return False, f"修改数据失败: {e}"

    def add_question(self, prompt, question_content, llm):
        """
        添加prompt和问题的内容
        prompt: string，内容
        question_content: string
        llm: list or string
        Returns:
        """
        # 处理成questions
        try:
            questions = []
            if isinstance(question_content, str):
                if question_content.startswith("[") and question_content.endswith("]"):
                    #  说明是json格式
                    questions = json.loads(question_content)
                else:
                    #  说明是纯文本文本格式
                    for one in question_content.split("\n"):
                        one = one.strip()
                        question = re.sub(r"\d+\.\s*", "", one)
                        questions.append(question)
            else:
                assert isinstance(question_content, list), "question_content必须为list或者str"
                questions = question_content
        except Exception as e:
            return False, f"数据无法按行进行处理,{e}"
        # 相同的prompt,只能有一个
        data = self.mongo.read_data(collection='question')
        for idx, one in enumerate(data):
            has_prompt = one["prompt"]
            if prompt == has_prompt:
                one_data = {
                    "$set": {
                        "llm": llm,
                        "prompt": prompt,
                        "question_content": question_content,
                        "questions": questions,
                    }
                }
                status, msg = self.mongo.update_one_data(collection='question',query={"prompt": prompt},new_values=one_data)
                return status, msg
        one_data = {
            "llm": llm,
            "prompt": prompt,
            "question_content": question_content,
            "questions": questions,
        }
        try:
            self.mongo.insert_data(data=[one_data], collection='question')
            # 更新下prompt
            return True, "插入数据成功"
        except Exception as e:
            logging.error(f"插入数据失败: {e}")
            return False, "插入数据失败"
    def append_one_question(self, prompt, question):
        """
        追加1个问题记录到prompt对应的问题库中
        prompt: string，内容
        question: string
        Returns:
        """
        # 相同的prompt,只能有一个
        data = self.mongo.read_data(collection='question')
        for idx, one in enumerate(data):
            has_prompt = one["prompt"]
            questions = one["questions"]
            questions.append(question)
            question_content = one["question_content"]
            if prompt == has_prompt:
                # 更新下question_content
                try:
                    if isinstance(question_content, str):
                        if question_content.startswith("[") and question_content.endswith("]"):
                            #  说明是json格式
                            ques = json.loads(question_content)
                            ques.append(question)
                            question_content = json.dumps(ques, ensure_ascii=False)
                        else:
                            #  说明是纯文本文本格式
                            question_content = question_content + "\n" + question
                    else:
                        assert isinstance(question_content, list), "question_content必须为list或者str"
                        question_content.append(question)
                except Exception as e:
                    return False, f"数据无法按行进行处理,{e}"
                one_data = {
                    "$set": {
                        "llm": one["llm"],
                        "prompt": prompt,
                        "question_content": question_content,
                        "questions": questions,
                    }
                }
                status, msg = self.mongo.update_one_data(collection='question',query={"prompt": prompt},new_values=one_data)
                return status, msg
        return False, f"没有找到对应该prompt{prompt}的问题库"

    def delete_question(self, prompt, llm):
        """
        删除prompt和问题的内容
        Args:
            prompt ():
            llm (): list or string
        Returns:
        """
        try:
            status, msg = self.mongo.delete_one_data(query={"prompt": prompt, "llm": llm}, collection='question')
            return status, msg
        except Exception as e:
            logging.error(f"删除数据失败: {e}")
            return False, f"删除数据失败: {e}"

    def get_all_questions(self, keyword="empty", namelength=False,norepeat=False):
        """
        获取所有questions,
        Args:
            keyword: 根据keyword搜索prompt，如果给定
            namelength: 只返回名称和长度，不返回实际的内容
            norepeat: 全局去重，和所有已标注的数据进行过滤，如果发现重复的，那么就跳过这条数据
        Returns:
        """
        data = self.mongo.read_data(collection='question')
        # id变成字符串，格式的
        result = []
        for idx, one in enumerate(data):
            prompt = one["prompt"]
            _id = one.pop("_id")
            data[idx]["id"] = str(_id)
            data[idx]["number"] = len(data[idx]["questions"])
            if namelength:
                #去掉questions和question_content，为了前端获取速度更快
                data[idx].pop("questions")
                data[idx].pop("question_content")
            gen_time = _id.generation_time
            # 创建一个代表UTC+8的时区
            tz_utc_8 = datetime.timezone(timedelta(hours=8))
            # 将当前时间转换为UTC+8时区（北京时间）
            gen_time = gen_time.astimezone(tz_utc_8)
            time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
            data[idx]["time"] = time_str
            if keyword == "empty":
                result.append(data[idx])
            elif keyword in prompt:
                if norepeat:
                    #需要和全局已标注数据进行去重
                    questions = one["questions"]
                    logging.info(f"启用重复数据过滤，原有数据: {len(questions)}条")
                    label_data = self.mongo.read_data(collection='label')
                    label_data_human_dict = {}
                    for one in label_data:
                        messages = one["messages"]
                        content = messages[0].get("content")
                        label_data_human_dict[content] = 1
                    for qidx, q in enumerate(questions):
                        if isinstance(q, dict):
                            content = q.get("content")
                        elif isinstance(q, str):
                            content = q
                        else:
                            raise Exception(f"不支持的问题类型，请检查问题的数据格式，是字符串或者json")
                        if content in label_data_human_dict:
                            #删除已标注的数据
                            del data[idx]["questions"][qidx]
                    logging.info(f'经过过滤后的数据，还剩: {len(data[idx]["questions"])}条')
                result.append(data[idx])
        return result

    def query_questions_label(self,questions):
        """
        TODO: 查询问题是否已经标注，返回已标注数据,依赖label和llmlabel这2个表的数据
        llmlabel中的数据可以用作偏好训练中的坏样本, label中的作为正样本
        Args:
            questions (): list， 多个问题，根据问题进行查询
        Returns:
        """
        llm_data = self.mongo.read_data(collection='llmlabel')
        human_data = self.mongo.read_data(collection='label')
        def process_data(data, label_type="llm"):
            result = []
            for idx, one in enumerate(data):
                one["status"] = label_type
                prompt = one["prompt"]
                _id = one.pop("_id")
                data[idx]["id"] = str(_id)
                gen_time = _id.generation_time
                # 创建一个代表UTC+8的时区
                tz_utc_8 = datetime.timezone(timedelta(hours=8))
                # 将当前时间转换为UTC+8时区（北京时间）
                gen_time = gen_time.astimezone(tz_utc_8)
                time_str = gen_time.strftime('%Y-%m-%d %H:%M:%S')
                data[idx]["time"] = time_str
                result.append(data[idx])
            return result
        llm_data = process_data(llm_data,label_type="llm")
        human_data = process_data(human_data, label_type="human")
        data = llm_data + human_data
        question2label = {}
        for idx, one in enumerate(data):
            # 和questions进行比较，找到是否标注了
            messages = one["messages"]
            first_role = messages[0]["role"]
            first_content = messages[0]["content"]
            if first_role in ["human", "user"]:
                question2label[first_content] = one
        result = []
        for question in questions:
            # 匹配到了标注
            match_label = question2label.get(question)
            one = {"question": question, "id": "", "messages": []}
            if match_label:
                one["status"] = match_label["status"] # 人工标注或者llm标注了
                one["id"] = match_label["id"]
                one["messages"] = match_label["messages"]
            else:
                one["status"] = "unlabeled"  #没有标注过
            result.append(one)
        return result
    
def jwt_required_with_whitelist(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        whitelist = ['127.0.0.1', '192.168.50.101', '10.8.0.6']  # 根据实际需求添加白名单
        ip = request.remote_addr
        logging.info(f"用户登录的ip是: {ip}")
        if ip in whitelist:
            return fn(*args, **kwargs)
        else:
            return jwt_required()(fn)(*args, **kwargs)

    return wrapper

@bp.route("/api/execute", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def execute_api():
    """
    调用工具
    print(dispatch_tool("get_weather", {"city_name": "beijing"}))
    print(get_tools())
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    if request.method == 'GET':
        jsonres = request.args
    else:
        jsonres = request.get_json()
    tool_name = jsonres.get("name")  # 工具名称是必须的
    tool_params = jsonres.get("arguments", {})  # 可以没有参数
    if tool_name is None:
        return jsonify({"code": 4001, "msg": "tool_name is required", "data": []})
    if isinstance(tool_params, str):
        try:
            tool_params = json.loads(tool_params)
        except Exception as e:
            logging.error(f"调用工具穿过来的工具调用参数解析错误: {e}, {tool_params}")
            return jsonify({"code": 4001, "msg": "tool_params can't parsed", "data": []})
    result = dispatch_tool(tool_name, tool_params)
    if jsonres.get('id'): #如果给的工具中携带工具的id，那么顺便给返回去，因为有时会调用同一个工具多次，所以会传过来id
        result["id"] = jsonres.get('id')
    result["name"] = tool_name
    status = result.get("status")
    if status:
        logging.info(f"执行工具成功: {tool_name}, {tool_params}, 返回的结果是: {result}")
        return jsonify({"code": 0, "msg": "success", "data": result})
    else:
        logging.error(f"执行工具失败: {tool_name}, {tool_params}, 返回的结果是: {result}")
        return jsonify({"code": 0, "msg": "success", "data": result})

@bp.route("/api/get_tools", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def tools_api():
    """
    获取所有的工具信息
    :return:
    :rtype:
    """
    tools = get_tools()
    return jsonify({"code": 0, "msg": "success", "data": tools})

@bp.route("/api/get_prompts", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def prompts_api():
    """
    获取所有的prompts
    :return:
    :rtype:
    """
    prompts = chatbot_instance.get_all_prompt()
    return jsonify({"code": 0, "msg": "success", "data": prompts})

@bp.route("/api/get_prompts_questions", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def prompts_questions_api():
    """
    获取所有的prompts
    :return:
    :rtype:
    """
    prompts_questions = chatbot_instance.get_all_prompt_questions()
    return jsonify({"code": 0, "msg": "success", "data": prompts_questions})

@bp.route("/api/query_questions_label", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def questions_label_api():
    """
    根据问题获取标注结果，人工或者llm标注的结果
    :return:
    {
    "code": 0,
        "data": [
            {
                "id": "65f00e2cc4e89880e8d4fd29",
                "question": "查询下IP59.82.21.45",
                "status": "human"
            },
            {
                "id": "6673e6288ba70b7b94801426",
                "question": "在低端的面部精华市场力里，前五名的品牌都有谁？",
                "status": "human"
            }
        ],
        "msg": "success"
    }
    :rtype:
    """
    jsonres = request.get_json()
    questions = jsonres.get("questions")  # 获取问题列表中的问题
    if questions is None:
        return jsonify({"code": 4002, "msg": "questions is required", "data": []})
    if not isinstance(questions, list):
        return jsonify({"code": 4002, "msg": "questions must be a list", "data": []})
    data = chatbot_instance.query_questions_label(questions)
    return jsonify({"code": 0, "msg": "success", "data": data})

@bp.route("/api/add_prompt", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def add_prompt_api():
    """
    获取所有的prompts
    :return:
    :rtype:
    """
    jsonres = request.get_json()
    name = jsonres.get("name")  # 使用哪个prompt
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    usage = jsonres.get("usage", "QA")  # 使用哪个prompt
    knowledge_base = jsonres.get("knowledge_base", "")  # 使用哪个prompt
    if name is None or prompt is None:
        return jsonify({"code": 4002, "msg": "name 和 prompt is required", "data": []})
    status, msg = chatbot_instance.add_prompt(name, prompt, usage, knowledge_base)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/delete_prompt", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def delete_prompt_api():
    """
    删除1条prompt，按名字删除
    :return:
    :rtype:
    """
    jsonres = request.get_json()
    name = jsonres.get("name")  # 使用哪个prompt
    if name is None:
        return jsonify({"code": 4002, "msg": "name is required", "data": []})
    status, msg = chatbot_instance.delete_prompt(name)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/modify_prompt", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def modify_prompt_api():
    """
    修改prompt的内容
    :return:
    :rtype:
    """
    jsonres = request.get_json()
    name = jsonres.get("name")  # 使用哪个prompt
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    usage = jsonres.get("usage")  # 使用哪个prompt
    knowledge_base = jsonres.get("knowledge_base", "")  # 使用哪个prompt
    if name is None or prompt is None or usage is None:
        return jsonify({"code": 4002, "msg": "name and prompt and usage is required", "data": []})
    status, msg = chatbot_instance.modify_prompt(name, prompt, usage, knowledge_base)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/label_chat", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def label_chat_api():
    """
    辅助标注的api
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    messages = jsonres.get("messages")
    llm = jsonres.get("llm", "chatgpt")
    tools = jsonres.get("tools", "empty")
    usecache = jsonres.get("usecache", True)
    # 开始回答
    response = chatbot_instance.start_label_chat(messages=messages, prompt=prompt, llm=llm, tools=tools, usecache=usecache)
    return jsonify({"code": 0, "msg": "success", "data": response})

@bp.route("/api/chat", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def chat_api():
    """
    直接的chat聊天
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    messages = jsonres.get("messages")
    llm = jsonres.get("llm", "chatgpt")
    tools = jsonres.get("tools", "empty")
    usecache = jsonres.get("usecache", True)
    verbose = jsonres.get("verbose", False) # 是否返回verbose信息，就是返回中间的推理过程
    additional = jsonres.get("additional")
    # 开始回答
    if additional:
        messages = chatbot_instance.merge_additional_to_messages(messages, additional)
    status, response = chatbot_instance.start_chat(messages=messages, prompt=prompt, llm=llm, tools=tools, usecache=usecache,verbose=verbose)
    if status:
        return jsonify({"code": 0, "msg": "success", "data": response})
    else:
        return jsonify({"code": 4006, "msg": response, "data": response})

@bp.route("/api/save_message", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def save_message_api():
    """
    保存一条标注数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    messages = jsonres.get("messages")
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    tools = jsonres.get("tools", None)  # 使用哪个prompt
    id = jsonres.get("id", None)
    collection = jsonres.get("collection", "label")  # 保存到哪个collection,默认保存到label的collection
    if messages is None or prompt is None:
        return jsonify({"code": 4002, "msg": "messages 和 prompt is required", "data": []})
    # 开始回答
    logging.info(f"收到数据: messages: {messages}, prompt: {prompt}, tools: {tools}")
    status, msg = chatbot_instance.save_messages(messages=messages, prompt=prompt, tools=tools,id=id,collection=collection)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/update_message", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def update_message_api():
    """
    更新一条标注数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    id = jsonres.get("id")
    messages = jsonres.get("messages")
    prompt_name = jsonres.get("prompt_name", "")  # 使用哪个prompt
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    tools = jsonres.get("tools")  # 使用哪个prompt
    if id is None or messages is None or prompt is None or tools is None:
        return jsonify({"code": 4002, "msg": "id, tools, messages 和 prompt is required", "data": []})
    # 开始回答
    # 对tools进行一下预处理
    if tools and isinstance(tools[0], dict):
        tools = [tool["name"] for tool in tools]  # 只要工具的名称
    status, msg = chatbot_instance.update_message(id=id, messages=messages, prompt_name=prompt_name, prompt=prompt, tools=tools)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/delete_message", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def delete_message_api():
    """
    删除一条message数据
    :return:
    :rtype:
    """
    logging.info(f"收到删除数据请求: {request}")
    jsonres = request.get_json()
    id = jsonres.get("id")
    if id is None:
        return jsonify({"code": 4002, "msg": "messages id is required", "data": []})
    # 开始回答
    status, msg = chatbot_instance.delete_message(id=id)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/query_message", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def query_message_api():
    """
    搜索message数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    mode = jsonres.get("mode", "simple")  # simple,detail
    limit = jsonres.get("limit", -1)  #
    keyword = jsonres.get("keyword")  #
    field = jsonres.get("field","all")  #
    if keyword is None:
        return jsonify({"code": 4002, "msg": "keyword is required", "data": []})
    # 开始回答
    data = chatbot_instance.query_messages(keyword,field=field,mode=mode,limit=limit)
    return jsonify({"code": 0, "msg": "success", "data": data})

@bp.route("/api/get_all", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def get_all_api():
    """
    获取所有数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    mode = jsonres.get("mode", "simple")  # simple,detail
    prompt = jsonres.get("prompt", "all")  # simple,detail
    limit = jsonres.get("limit", -1)  # simple,detail
    # 开始回答
    data = chatbot_instance.get_all_messages(mode=mode, limit=limit, prompt=prompt)
    return jsonify({"code": 0, "msg": "success", "data": data})

@bp.route("/api/get_all_number", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def get_all_number_api():
    """
    获取标注数量的总数
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    # 开始回答
    data = chatbot_instance.get_total_messages_number()
    return jsonify({"code": 0, "msg": "success", "data": data})


@bp.route("/api/clear", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def clear_api():
    """
    清理数据库
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    # 开始回答
    chatbot_instance.clear_mongo_db()
    return jsonify({"code": 0, "msg": "success", "data": "ok"})


@bp.route("/api/valid_message", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def api_valid_message():
    """
    验证message是否合法
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    messages = jsonres.get("messages")
    if messages is None:
        return jsonify({"code": 4002, "msg": "messages is required", "data": []})
    # 开始回答
    status, msg = chatbot_instance.valid_messages(messages=messages)
    if status:
        return jsonify({"code": 0, "msg": "success", "data": msg})
    else:
        return jsonify({"code": 4003, "msg": "failed", "data": msg})


@bp.route("/api/get_llm", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def get_llm_api():
    """
    获取llm的名称
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    # 开始回答
    data = chatbot_instance.get_llm_status()
    return jsonify({"code": 0, "msg": "success", "data": data})


@bp.route("/api/export", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def export_api():
    """
    导出数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    # 开始回答
    data = chatbot_instance.export_all_data()
    return jsonify({"code": 0, "msg": "success", "data": data})


@bp.route("/api/generate_question", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def generate_question_api():
    """
    sample菜单使用：根据用户的prompt生成一些sample的问题
    :return:
    :rtype:
    """
    logging.info(f"收到generate_question的请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # prompt的名称或者文本内容
    tool_name = jsonres.get("tool_name")  # prompt结合工具名称生成对应的问题
    usecache = jsonres.get("usecache", True)  # prompt结合工具名称生成对应的问题
    llm = jsonres.get("llm", ["chatgpt"])  # prompt结合工具名称生成对应的问题, list or string
    if prompt is None:
        return jsonify({"code": 4002, "msg": "prompt is required", "data": []})
    # 开始回答
    status, msg, data = chatbot_instance.generate_question_sample(prompt, tool_name, llm, usecache)
    if status:
        return jsonify({"code": 0, "msg": "success", "data": data})
    else:
        return jsonify({"code": 4001, "msg": msg, "data": []})

@bp.route("/api/append_question", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def append_question_api():
    """
    保存生成的问题,支持按行保存的text和python的列表格式数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    question = jsonres.get("question") # 单个问题，被追加
    if prompt is None or question is None:
        return jsonify({"code": 4002, "msg": "prompt和question is required", "data": []})
    status, msg = chatbot_instance.append_one_question(prompt, question)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})

@bp.route("/api/save_question", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def save_question_api():
    """
    保存生成的问题,支持按行保存的text和python的列表格式数据
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    question_content = jsonres.get("question_content")
    llm = jsonres.get("llm")  # 使用哪个prompt, list, []
    if prompt is None or question_content is None or llm is None:
        return jsonify({"code": 4002, "msg": "prompt和question_content 和 llm is required", "data": []})
    status, msg = chatbot_instance.add_question(prompt, question_content, llm)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/delete_question", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def delete_question_api():
    """
    删除已保存的问题
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    prompt = jsonres.get("prompt")  # 使用哪个prompt
    llm = jsonres.get("llm")  # 使用哪个prompt
    if prompt is None or llm is None:
        return jsonify({"code": 4002, "msg": "prompt 和 llm is required", "data": []})
    # 开始回答add_question(self, prompt, question_content, llm)
    status, msg = chatbot_instance.delete_question(prompt, llm)
    if status:
        return jsonify({"code": 0, "msg": msg, "data": status})
    else:
        return jsonify({"code": 4003, "msg": msg, "data": status})


@bp.route("/api/get_all_questions", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def get_all_questions_api():
    """
    获取所有的问题
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    keyword = jsonres.get("keyword", "empty")  # 使用哪个prompt
    norepeat = jsonres.get("norepeat", False)  # 是否去重
    namelength = jsonres.get("namelength", False)  # 只返回名称和数量，不返回实际的问题内容
    data = chatbot_instance.get_all_questions(keyword,namelength,norepeat)
    return jsonify({"code": 0, "msg": "success", "data": data})


@bp.route("/api/backup", methods=['GET', 'POST'])
@jwt_required_with_whitelist
def backup_api():
    """
    备份数据库
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    data = chatbot_instance.backup_mongo()
    return jsonify({"code": 0, "msg": "success", "data": data})

@bp.route("/neo4j/query", methods=['POST'])
def neo4j_query_api():
    """
    查询neo4j的数据库
    :return:
    :rtype:
    """
    logging.info(f"收到请求: {request}")
    jsonres = request.get_json()
    property_name = jsonres.get("property_name")  # 节点的属性名称
    property_value = jsonres.get("property_value")  # 节点的属性值，例如节点的id为东北日记
    limit = jsonres.get("limit",20)  # 节点的属性值，例如节点的id为东北日记
    if id is None:
        return jsonify({"code": 4002, "msg": "节点的id没有给定", "data": []})
    data = food_instance.query_by_property(property_name,property_value,limit=limit)
    return jsonify({"code": 0, "msg": "success", "data": data})


food_instance = FoodNeo4j()
chatbot_instance = ChatBot()
