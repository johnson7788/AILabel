"""
这段代码是工具注册的部分，通过注册工具，让模型实现工具调用
代码来自ChatGLM3/tools_using_demo/tool_register.py
# 依赖: gevent-websocket
"""
import os
import time
from datetime import timedelta
import logging
import argparse
import json
import re
from flask import Flask, request, jsonify, abort, render_template, Response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_cors import CORS
from route_label import bp as label_bp
from route_basic import bp as basic_bp

app = Flask(__name__, static_url_path="", static_folder='data')
CORS(app, supports_credentials=True)
app.config["JWT_SECRET_KEY"] = "ZGQgaWY9L2Rldi91cmFuZG9tIGJzPT"  # 随机key比较好
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60 * 24 * 7)
jwt = JWTManager(app)

if not os.path.exists('logs'):
    os.mkdir('logs')
logfile = "logs/toolapi.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(logfile, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
# 注册页面
app.register_blueprint(basic_bp) # 基本api
app.register_blueprint(label_bp) # 标注相关

def parse_args():
    """
    返回arg变量和help
    :return:
    """
    parser = argparse.ArgumentParser(description="工具使用API")
    parser.add_argument('-p', '--port', type=int, default=5556, help='端口')
    return parser.parse_args(), parser.print_help

if __name__ == "__main__":
    args, helpmsg = parse_args()
    app.run(host='0.0.0.0', port=args.port, threaded=True)
    # res = determine_advertisement(comment="这条裙子真好看！")
    # print(res)
