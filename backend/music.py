"""
Author: flwfdd
Date: 2021-12-23 23:38:26
LastEditTime: 2023-01-15 20:56:24
Description: 音乐模块
_(:з」∠)_
"""

# -*- coding: utf-8 -*-
import requests
import json
import time
import os
import config
from flask import abort

header = config.header
api_url = config.api_base_url.copy()  # https://music.163.com/api/search/get/web
check_tmp = config.check_tmp
save_tmp = config.save_tmp


# 网易云


def cloud_user(mid):
    url = api_url["C"] + "/user/playlist?uid=" + mid + "&cookie=" + config.C_vip_cookie
    print(url)
    r = requests.get(url)
    dic = json.loads(r.text)["playlist"]

    for ind, i in enumerate(dic):
        x = {}
        x["type"] = "list"
        x["mid"] = "C" + str(i["id"])
        x["name"] = i["name"]
        x["artist"] = [i["creator"]["nickname"]]
        x["album"] = {"name": ""}
        dic[ind] = x
    return dic


def cloud_list(mid):
    url = "https://music.163.com/api/playlist/detail?id=" + mid
    print(url)
    r = requests.get(url)
    dic = json.loads(r.text)
    result_list = []
    if dic["code"] == -447:  # 服务器忙碌，请稍后再试
        # return abort(400, dic["msg"])
        x = {}
        x["type"] = "msg"
        x["mid"] = "0"
        x["name"] = dic["msg"]
        x["artist"] = []
        x["album"] = {"name": "网易云被玩坏了,这不是MergeMusic的问题,绝对不是(；´д｀)"}
        x["vip"] = False
        result_list.append(x)
        y = {}
        y["type"] = "msg"
        y["mid"] = "0"
        y["name"] = "尝试收起并重新展开列表可能解决问题"
        y["artist"] = []
        y["album"] = {"name": "提示"}
        y["vip"] = False
        result_list.append(y)
    else:  # code 200
        raw_list = dic["result"]["tracks"]

        for ind, i in enumerate(raw_list):  # ind索引 i对象
            x = {}
            x["type"] = "music"
            x["mid"] = "C" + str(i["id"])
            x["name"] = i["name"]
            x["artist"] = [j["name"] for j in i["artists"]]
            x["album"] = {"name": i["album"]["name"]}
            x["vip"] = True if i["fee"] == 1 else False
            result_list.append(x)

    return result_list


def cloud_music(mid):
    dic = {
        "lrc": "",
        "tlrc": "",
        "src": "",
        "img": "",
        "type": "music",
        "mid": "C" + mid,
    }

    # 获取播放链接
    try:
        # data = {"id": mid, "cookie": config.C_vip_cookie}
        r = requests.get(f"https://music.163.com/api/song/detail?ids=[{mid}]")
        data = json.loads(r.text)
        if data["songs"][0]["fee"] == 1:
            # 外链获取URL的方法无法播放VIP音乐
            dic["src"] = ""
        else:
            dic["src"] = f"http://music.163.com/song/media/outer/url?id={mid}.mp3"
    except:
        dic["src"] = ""
    if not dic["src"]:
        dic["src"] = ""

    # 获取图片和基础信息
    try:
        # data = {"ids": mid, "cookie": config.C_vip_cookie}
        url = f"https://music.163.com/api/song/detail?ids=[{mid}]"
        info = json.loads(requests.get(url=url).text)["songs"][0]
        dic["name"] = info["name"]
        dic["artist"] = [i["name"] for i in info["artists"]]
        dic["album"] = {"name": info["album"]["name"]}
        dic["img"] = info["album"]["picUrl"]
    except:
        dic["img"] = ""

    # TODO: 获取歌词
    try:
        url = f"https://music.163.com/api/song/media?id={mid}"
        dic["lrc"] = json.loads(requests.get(url).text)["lyric"]

        # dic["tlrc"] = json.loads(
        #     requests.get(
        #         api_url["C"] + "/lyric/?id=" + mid + "&cookie=" + config.C_vip_cookie
        #     ).text
        # )["tlyric"]["lyric"]
    except:
        dic["lrc"] = "[00:0.00]木有歌词哦"

    return dic


def cloud(mid, Type):
    if Type == "list":
        dic = cloud_list(mid)
    elif Type == "music":
        dic = cloud_music(mid)
    elif Type == "user":
        dic = cloud_user(mid)
    else:
        dic = []

    return dic


# QQ


def qq_get_detail(qq_mid):
    data = {
        "songinfo": {
            "method": "get_song_detail_yqq",
            "module": "music.pf_song_detail_svr",
            "param": {"song_mid": qq_mid},
        }
    }
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode("utf-8"))
    dic = r.json()["songinfo"]["data"]["track_info"]

    return {
        "type": "music",
        "mid": "Q" + qq_mid,
        "name": dic["name"],
        "artist": [j["name"] for j in dic["singer"]],
        "album": {"name": dic["album"]["name"]},
        "img": "https://y.gtimg.cn/music/photo_new/T002R500x500M000{}.jpg".format(
            dic["album"]["mid"]
        ),
        "media_mid": dic["file"]["media_mid"],
    }


def qq_get_src(qq_mid, qq_media_mid):
    data = {
        "req_0": {
            "module": "vkey.GetVkeyServer",
            "method": "CgiGetVkey",
            "param": {
                "filename": ["M500{}.mp3".format(qq_media_mid)],
                "guid": "2333",
                "songmid": [qq_mid],
                "songtype": [0],
                "loginflag": 1,
                "platform": "20",
            },
        },
        "comm": {"format": "json", "ct": 24, "cv": 0},
    }
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode("utf-8"))
    data = r.json()["req_0"]["data"]
    purl = data["midurlinfo"][0]["purl"]
    if purl:
        return data["sip"][0] + purl
    else:
        return ""


def qq_get_lrc(qq_mid):
    data = "format=json&nobase64=1&g_tk=5381&songmid=" + qq_mid
    r = requests.post(
        "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg",
        data=data,
        headers={"Referer": "y.qq.com"},
    )
    data = r.json()
    return {"lrc": data["lyric"], "tlrc": data["trans"]}


def qq_music(mid):
    dic = {
        "lrc": "",
        "tlrc": "",
        "src": "",
        "img": "",
        "type": "music",
        "mid": "Q" + mid,
    }

    # 获取基本信息
    try:
        dic = qq_get_detail(mid)
    except:
        return dic

    # 获取播放链接
    try:
        dic["src"] = qq_get_src(mid, dic["media_mid"])
    except:
        dic["src"] = ""

    # 获取歌词
    try:
        data = qq_get_lrc(mid)
        dic["lrc"], dic["tlrc"] = data["lrc"], data["tlrc"]
    except:
        dic["lrc"], dic["tlrc"] = "[00:0.00]木有歌词哦", ""

    return dic


def qq(mid, Type):
    if Type:
        dic = qq_music(mid)

    return dic


# bili


def bili_get_vid(vid):  # 获取视频详情
    if vid[0] == "B":
        r = requests.get(
            "https://api.bilibili.com/x/web-interface/view?bvid=" + vid, headers=header
        )
    else:
        r = requests.get(
            "https://api.bilibili.com/x/web-interface/view?aid=" + vid[2:],
            headers=header,
        )
    return json.loads(r.text)


# def bili_get_playinfo(vid):  # 获取播放链接
#     r = requests.get("https://www.bilibili.com/video/" + vid, headers=header)
#     s = r.text
#     p = s.find("playinfo__=")
#     s = s[p + 11 :]
#     p = s.find("</script>")
#     s = s[:p]
#     return json.loads(s)


def bili_get_playinfo(vid):  # 获取播放链接
    p = vid[vid.find("?p=") + 3 :]  # 获取请求的分p数
    url = f"https://api.bilibili.com/x/web-interface/view?aid={vid[2:vid.find('?p=')]}"
    r = requests.get(url, headers=header)
    data = json.loads(r.text)["data"]
    bvid = data["bvid"]
    cid = data["pages"][int(p) - 1]["cid"]
    url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=0&fnver=0&fnval=4048&fourk=1"
    r = requests.get(url, headers=header)
    return json.loads(r.text)


def bili_get_audio(vid):  # 获取音频
    header["Referer"] = "https://www.bilibili.com"
    dic = bili_get_playinfo(vid)
    url = dic["data"]["dash"]["audio"][0]["baseUrl"]
    filename = vid.replace("?p=", "_")
    # r = requests.head(url, headers=head)
    # if(int(r.headers['Content-Length'])>30*1024*1024): 0/0
    r = requests.get(url, headers=header)
    return save_tmp(filename + ".m4a", r.content)


def bili_get_img(vid):  # 获取封面图
    info = bili_get_vid(vid)
    bin = requests.get(info["data"]["pic"], headers=header).content
    # f.write(requests.get(info['data']['pic']+"@233w_233h.jpg").content)
    return save_tmp(vid + ".jpg", bin)


def bili_get_user_fav(uid):  # 获取用户收藏列表
    url = (
        "https://api.bilibili.com/x/v3/fav/folder/created/list?pn=1&ps=100&up_mid="
        + uid
    )
    r = requests.get(url, headers=header)
    return json.loads(r.text)


def bili_get_fav(mid):  # 获取收藏夹内容
    url = (
        "https://api.bilibili.com/x/v3/fav/resource/list?media_id={}&ps=20&pn=".format(
            mid
        )
    )
    dic = json.loads(requests.get(url, headers=header).text)
    mm = dic["data"]["info"]["media_count"] - 20
    c = 2
    while mm > 0:
        mdic = json.loads(requests.get(url + str(c), headers=header).text)
        dic["data"]["medias"] += mdic["data"]["medias"]
        c += 1
        mm -= 20
    return dic


def bili_get_up_vid(uid):  # 获取up主作品列表
    url = "https://api.bilibili.com/x/space/arc/search?ps=50&mid=" + uid + "&pn="
    c = 1
    r = requests.get(url + str(c), headers=header)
    dic = json.loads(r.text)
    while len(dic["data"]["list"]["vlist"]) < dic["data"]["page"]["count"]:
        c += 1
        r = requests.get(url + str(c), headers=header)
        mdic = json.loads(r.text)
        dic["data"]["list"]["vlist"] += mdic["data"]["list"]["vlist"]
    return dic


def bili(mid, Type):
    vid = mid
    if Type == "p":  # 可能带有多P的视频
        if vid.find("?") != -1:
            vid = vid[: vid.find("?")]
        dic = bili_get_vid(vid)["data"]
        l = []
        for i in dic["pages"]:
            x = {}
            x["type"] = "music"
            x["name"] = dic["title"] + "-" + i["part"]
            x["mid"] = "Bav" + str(dic["aid"]) + "_" + str(i["page"])
            x["album"] = {"name": ""}
            x["artist"] = [dic["owner"]["name"]]
            l.append(x)
        return l
    elif Type == "music":  # 单个分P
        if vid.find("_") == -1:
            vid += "_1"
        p = int(vid[vid.find("_") + 1 :])
        vid = vid[: vid.find("_")]
        info = bili_get_vid(vid)["data"]
        vid = "av" + str(info["aid"])

        audio_name = vid + "_" + str(p) + ".m4a"
        src = check_tmp(audio_name)
        if not src:
            src = bili_get_audio(vid + "?p=" + str(p))

        img_name = vid + ".jpg"
        img = check_tmp(img_name)
        if not img:
            img = bili_get_img(vid)

        if info["title"] == info["pages"][min(p, len(info["pages"])) - 1]["part"]:
            p_name = info["title"]
        else:
            p_name = (
                info["title"]
                + " - "
                + info["pages"][min(p, len(info["pages"])) - 1]["part"],
            )

        dic = {
            "type": "music",
            "mid": "B" + vid + "_" + str(p),
            "src": src,
            "img": img,
            "lrc": "[00:00.00]木有歌词哦",
            "album": {"name": ""},
            "artist": [info["owner"]["name"]],
            "name": p_name,
        }
        return dic
    elif Type == "user":  # 用户
        dic = bili_get_user_fav(vid)
        try:
            dic = dic["data"]["list"]
        except:
            dic = []
        for ind, i in enumerate(dic):
            x = {}
            x["type"] = "fav"
            x["name"] = i["title"]
            x["mid"] = "B" + str(i["id"])
            x["album"] = {"name": ""}
            x["artist"] = []
            dic[ind] = x
        mdic = bili_get_up_vid(vid)
        if mdic["data"]["page"]["count"] != 0:
            y = {
                "type": "up",
                "name": "投稿",
                "mid": "B" + vid,
                "album": {"name": ""},
                "artist": [],
            }
            dic = [y] + dic
        return dic
    elif Type == "fav":  # 收藏夹
        dic = bili_get_fav(vid)
        dic = dic["data"]["medias"]
        for ind, i in enumerate(dic):
            x = {}
            x["type"] = "p"
            x["name"] = i["title"]
            x["mid"] = "Bav" + str(i["id"])
            x["album"] = {"name": ""}
            x["artist"] = [i["upper"]["name"]]
            x["p"] = i["page"]
            dic[ind] = x
        return dic
    elif Type == "up":  # up主
        dic = bili_get_up_vid(vid)
        dic = dic["data"]["list"]["vlist"]
        for ind, i in enumerate(dic):
            x = {}
            x["type"] = "p"
            x["name"] = i["title"]
            x["mid"] = "Bav" + str(i["aid"])
            x["album"] = {"name": ""}
            x["artist"] = [i["author"]]
            dic[ind] = x
        return dic


# 入口函数
def main(dic):
    mid = dic["mid"]
    Type = dic["type"]

    platform = mid[0]
    mid = mid[1:]

    if platform == "C":
        res = cloud(mid, Type)
    elif platform == "Q":
        res = qq(mid, Type)
    elif platform == "B":
        if mid[0].isdigit():
            mid = "av" + mid
        res = bili(mid, Type)
    else:
        return abort(400, "Invalid Params")

    return json.dumps(res, ensure_ascii=False)
