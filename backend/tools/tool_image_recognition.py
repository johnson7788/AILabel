#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/4/26 14:08
# @File  : tool_image_recognition.py
# @Author: 
# @Desc  :
import requests
import json
from typing import Annotated

tool_meta = {
    "group": "图片处理", # 分组
    "example": '使用ram_plus模型识别图片： image_recognition(image="https://ts1.cn.mm.bing.net/th/id/Golden-Gate-Bridge.jpg", model="ram_plus")',  # 示例
    "composed": "", # 组合说明
}

def image_recognition(
        image: Annotated[str, '一张图片的url', True],
        model: Annotated[str, '使用哪种模型: blip or ram_plus', False] = "ram_plus",
) -> str:
    """
    给出图片链接，返回图片中识别出的内容
    """
    if not isinstance(image, str):
        raise TypeError("图片必须是字符串格式的")
    if "http" not in image:
        raise ValueError("图片链接必须以http或者https开头的链接")
    if "model" not in ["blip", "ram_plus"]:
        raise ValueError("model参数必须是blip或者ram_plus")
    try:
        url = f"http://192.168.50.209:6351/api/predict"
        data = {"image": image, "model": model}
        # 提交form格式数据
        headers = {'content-type': 'application/json'}
        # 提交form格式数据
        r = requests.post(url, data=json.dumps(data), headers=headers)
        ret = r.json()
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error：执行图片理解的接口错误!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}
