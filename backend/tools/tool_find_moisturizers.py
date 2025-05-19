#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/4/26 14:08
# @File  : tool_find_moisturizers.py
# @Author: 
# @Desc  : 查找含有某个成分的产品，可以自定义成分的含量
from typing import Annotated
from py2neo import Graph

# 在这里填写图数据库的连接信息
host = "l0"
user = "neo4j"
password = "welcome123"
database = "neo4j"

tool_meta = {
    "group": "美妆图谱", # 分组
    "example": '例如找到所有药监局备案信息里标注视黄醇为主要备案成分的面霜产品（主要成分定义：含量>0.1%）: get_weather(find_product="视黄醇",category="面霜")',  # 示例
    "composed": "", # 和其它函数的组合说明
}

def find_moisturizers(ingredient: Annotated[str, '成分名', True],
				 category: Annotated[str, '品类', True],
				 concentration: Annotated[float, '含量占比', False] = 0.1
) -> str:
    """
    根据品类，成分，占比，搜索商品
    """
    if not isinstance(ingredient, str):
        raise TypeError("成分必须是字符串格式的")
    if not isinstance(category, str):
        raise TypeError("品类必须是字符串格式的")
    try:
        graph = Graph(host=host, user=user, password=password, name=database)
        # query = f"MATCH (p:Product)-[:CONTAINS]->(i:Ingredient {{name: '{ingredient}'}}) WHERE i.volume_heat > {concentration} " \
        #         f"RETURN p.name"
        query = f"MATCH (product:Product)-[:CONTAINS]->(component:Ingredient) WHERE component.name =~ '.*{ingredient}.*' RETURN product"
        print(f"运行的CQL是: {query}")
        result = graph.run(query).to_table()
        ret = [record[0] for record in result]
        return {"msg": ret, "need_summary": True, "status": True}
    except:
        import traceback
        ret = "Error：执行品类成分查找商品的接口错误!\n" + traceback.format_exc()
        return {"msg": ret, "need_summary": True, "status": False}