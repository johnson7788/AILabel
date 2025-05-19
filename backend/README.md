# 标注工具的后端
## 启动
python main.py

## 启动不同的模型适配
python openai_api.py
python ollama_api.py
python zhipuai_api.py

## 依赖mongo数据库存储标注数据

## 登录的用户名和密码
admin/admin

# 需要改进
1. 工具改成MCP
2. 嵌入模型替换成符合标准格式的
3. 写死的配置需要写成环境变量或配置文件
