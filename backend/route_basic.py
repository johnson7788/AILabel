#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/7/16 15:20
# @File  : route_basic.py
# @Author: 
# @Desc  : 基本页面
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

bp = Blueprint('basic', __name__)

@bp.route("/ping", methods=['GET', 'POST'])
def ping():
    """
    测试
    :return:
    :rtype:
    """
    return jsonify("Pong")

@bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username not in ["admin"]:  # you should verify username and password with your database's data
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)