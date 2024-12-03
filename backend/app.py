"""
Author: flwfdd
Date: 2022-01-03 13:33:31
LastEditTime: 2022-01-04 23:38:44
Description: 物理服务器Flask
_(:з」∠)_
"""

import os
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory
import search
import music
import signal
import psutil

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
    print(f"Get Font: {filename}")
    file = ""
    if filename == "materialdesignicons-webfont.woff2":
        print("1")
        file = "materialdesignicons-webfont.woff2"
    elif filename == "materialdesignicons-webfont.woff":
        print("2")
        file = "materialdesignicons-webfont.woff"
    elif filename == "materialdesignicons-webfont.ttf":
        print("3")
        file = "materialdesignicons-webfont.ttf"
    else:
        print("error")
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


# 音乐缓存下载服务
@app.route("/cache/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
