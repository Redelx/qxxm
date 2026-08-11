# -*- coding: utf-8 -*-
import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 唯一 CORS 配置

# ================= 配置区 =================
ARK_API_KEY = os.environ.get("ARK_API_KEY")
if not ARK_API_KEY:
    print("❌ 环境变量 ARK_API_KEY 未设置")

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seedream-5-0-lite-260128"
# ==========================================

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/transform', methods=['POST'])
def transform_image():
    try:
        if not ARK_API_KEY:
            return jsonify({"success": False, "error": "服务器配置错误：ARK_API_KEY 未设置"}), 500

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
            "size": "1K",
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
        response = requests.post(api_url, headers=headers, json=payload, timeout=90)

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

# 注意：不要添加 app.run()
