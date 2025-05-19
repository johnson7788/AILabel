#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/4/26 14:35
# @File  : tool_get_weather.py
# @Author: 
# @Desc  :
import requests
import json
from typing import Annotated

tool_meta = {
    "group": "日常", # 分组
    "example": '获取北京的天气： get_weather(city_name="北京")',  # 示例
    "composed": "", # 组合说明
}

def get_weather(
        city_name: Annotated[str, 'The name of the city to be queried', True],
) -> str:
    """
    根据给出的城市名字查询天气
    """
    if not isinstance(city_name, str):
        raise TypeError("City name must be a string")

    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
    }
    try:
        resp = requests.get(f"https://wttr.in/{city_name}?format=j1",timeout=5)
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "获取天气的接口异常!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}