"""
Author: flwfdd
Date: 2022-01-03 13:33:31
LastEditTime: 2022-01-04 23:38:44
Description: 物理服务器Flask
_(:з」∠)_
"""

import os
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory, send_file, abort
import search
import music
import signal
import psutil
import requests
from io import BytesIO
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app, resources=r"/*")


@app.route("/server_api/<api>", methods=["GET"])
def server_api(api):
    if api == "sys_info":
        info = {
            "pid": str(os.getpid()),
            "cpu": str(psutil.cpu_percent()) + "%",
            "memory": str(psutil.virtual_memory().percent) + "%",
        }
        return jsonify(info)
    elif api == "shutdown":
        passwd = request.args.get("passwd", default="")
        if passwd == "w@qwe5283":
            print("shutdown")
            os.kill(os.getpid(), signal.SIGTERM)
            return jsonify("accept")
        else:
            return jsonify("denied")


@app.route("/")
def say_hello():
    return send_from_directory("..", "index.html")
    # return "Hello MergeMusic!"


@app.route("/cdn_cache/<filename>")
def cdn_cache(filename):
    return send_from_directory("../cdn_cache/", filename)


@app.route("/fonts/<filename>", methods=["GET"])
def fonts_cache(filename):
    file = ""
    if filename == "materialdesignicons-webfont.woff2":
        file = "materialdesignicons-webfont.woff2"
    elif filename == "materialdesignicons-webfont.woff":
        file = "materialdesignicons-webfont.woff"
    elif filename == "materialdesignicons-webfont.ttf":
        file = "materialdesignicons-webfont.ttf"
    else:
        abort(400, "Invalid Fonts Requests")
    return send_from_directory("../cdn_cache/fonts/", file)


# 搜索服务
@app.route("/search/", methods=["GET", "POST"])
def search_():
    dic = request.values.to_dict()
    res = search.main(dic)

    return res


# 音乐服务
@app.route("/music/", methods=["GET", "POST"])
def music_():
    dic = request.values.to_dict()
    res = music.main(dic)

    return res


# 缓存文件储存
app.config["UPLOAD_FOLDER"] = "../music_cache"


# 图标
@app.route("/favicon.ico")
def get_icon():
    return send_from_directory("..", "favicon.ico")


ALLOWED_DOMAINS = ["music.126.net", "y.gtimg.cn"]


# 验证URL的有效性和安全性, 防止SSRF攻击
def is_valid_domain(url):
    parsed_uri = urlparse(url)
    domain = "{uri.netloc}".format(uri=parsed_uri)
    return any(domain.endswith(d) for d in ALLOWED_DOMAINS)


# 处理跨域显示图片
@app.route("/pic_proxy/", methods=["GET"])
def get_pic():
    pic_url = request.args.get("pic_url", "")

    # 验证URL的有效性和安全性, 防止SSRF攻击
    if not pic_url or not is_valid_domain(pic_url):
        return abort(400, "Invalid URL")

    try:
        res = requests.get(pic_url, timeout=5)
        res.raise_for_status()  # 检查请求是否成功

        if "image" in res.headers["content-type"]:
            return send_file(
                BytesIO(res.content),
                mimetype=res.headers["content-type"],
                as_attachment=False,
                download_name=pic_url.split("/")[-1],
            )
    except requests.RequestException as e:
        return abort(500, str(e))


# 音乐缓存下载服务
@app.route("/cache/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
