# -*- coding: utf-8 -*-
import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 显式配置 CORS，允许所有来源和 OPTIONS 方法
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# ================= 配置区 =================
# 从环境变量读取，不再硬编码
ARK_API_KEY = os.environ.get("ARK_API_KEY")
if not ARK_API_KEY:
    raise ValueError("环境变量 ARK_API_KEY 未设置！")

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seedream-5-0-lite-260128"
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return "✅ 后端服务已启动！AI 图片生成接口位于 /api/transform"

@app.route('/api/transform', methods=['POST', 'OPTIONS'])
def transform_image():
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 正常 POST 逻辑
    try:
        data = request.json
        image_base64 = data.get("image")
        style_prompt = data.get("style", "彝绣风格，红黄蓝配色，几何纹样，刺绣质感")

        if not image_base64:
            return jsonify({"success": False, "error": "没有收到图片"}), 400

        image_base64 = image_base64.strip().replace('\n', '').replace('\r', '')
        image_data_uri = f"data:image/jpeg;base64,{image_base64}"

        payload = {
            "model": MODEL,
            "prompt": f"将这张图片的风格转换为{style_prompt}。保持原图的内容、构图、物体和布局完全不变，只改变纹理、色彩和艺术风格。",
            "image": image_data_uri,
            "size": "2K",
            "output_format": "png",
            "response_format": "url",
            "watermark": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_API_KEY}"
        }

        api_url = f"{BASE_URL}/images/generations"
        print(f"⏳ 正在调用 Seedream 5.0 Lite...")
        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            image_url = result.get("data", [{}])[0].get("url")
            if image_url:
                print("✅ 图片生成成功！")
                return jsonify({"success": True, "image_url": image_url})
            else:
                return jsonify({"success": False, "error": "API 返回数据格式异常"}), 500
        else:
            error_msg = f"火山引擎 API 返回错误: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            print(f"❌ {error_msg}")
            return jsonify({"success": False, "error": error_msg}), response.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# 全局错误处理，确保返回 JSON
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "请求方法不允许，请使用 POST"}), 405

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "接口地址不存在"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000)) # Render 会通过环境变量提供端口
    app.run(host='0.0.0.0', port=port)      # 监听所有网络接口
