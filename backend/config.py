"""
Author: flwfdd
Date: 2022-01-03 13:44:03
LastEditTime: 2023-01-15 20:47:41
Description: 配置文件
_(:з」∠)_
"""

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66",
}

api_base_url = {
    "C": "https://music.163.com/api/search/get/web",  # 网易云音乐API
}

# 切换工作目录确保相对路径正常工作
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# bilibili歌曲缓存，需要存入歌曲并提供url
if True:
    from pathlib import Path

    storage_path = "../music_cache/"

    # 检查缓存文件是否存在，如果存在返回链接，否则返回空字符串
    def check_tmp(filename):
        if Path(storage_path + filename).is_file():
            return "/cache/" + filename
        else:
            return ""

    # 储存文件并返回链接
    def save_tmp(filename, bin):
        with open("../music_cache/" + filename, "wb") as file:
            file.write(bin)
            file.flush()
        return "/cache/" + filename


# 网易云账号cookie
C_vip_cookie = ""
# QQ音乐账号cookie
# Q_vip_cookie = ""
