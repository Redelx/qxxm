# netlify/functions/api.py
from serverless_wsgi import handle
# 从你的 Flask 应用文件中导入 app 实例
# 假设你的 Flask app 实例在 app.py 中名为 app
from app import app

def handler(event, context):
    # serverless_wsgi 的 handle 函数会处理 Flask 和 Netlify 之间的转换
    return handle(app, event, context)