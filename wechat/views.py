from django.shortcuts import render
from django.http import HttpResponse
import hashlib
import xml.etree.ElementTree as ET
import time
import logging
import requests

logger = logging.getLogger(__name__)


def index(request):
    if request.method == "GET":
        signature = request.GET.get('signature', "")
        timestamp = request.GET.get('timestamp', "")
        nonce = request.GET.get('nonce', "")
        echostr = request.GET.get('echostr', "")
        if not (signature and timestamp and nonce and echostr):
            return HttpResponse("error")
        token = "wgj"  # 请按照公众平台官网\基本配置中信息填写

        list1 = [token, timestamp, nonce]
        list1.sort()
        str_list = "".join(list1)
        sha1 = hashlib.sha1()
        sha1.update(str_list.encode())
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("not match!")


def handle_text(word):
    url = "http://fy.webxml.com.cn/webservices/EnglishChinese.asmx/TranslatorString?wordKey={}".format(word)
    res = requests.get(url)
    root = ET.fromstring(res.text)

    return root[3].text


def handle(request):
    if request.method == "POST":
        data = request.body.decode()
        logger.log(level=1, msg=data)
        root = ET.fromstring(data)
        gz = root.find("ToUserName").text
        user = root.find("FromUserName").text
        msg_type = root.find("MsgType").text

        if msg_type == "text":
            content = root.find("Content").text
            context = {
                "gz": gz,
                "user": user,
                "content": handle_text(content),
                "time": round(time.time(), 0)
            }
            return render(request, 'wechat/text.xml', context, content_type="text/xml")
        elif msg_type == "event":
            event = root.find("Event").text
            event_key = root.find("EventKey").text
            if event == "CLICK" and event_key == "weather":
                context = {
                    "gz": gz,
                    "user": user,
                    "content": "明天天气很好哟！",
                    }
                return render(request, 'wechat/text.xml', context, content_type="text/xml")
            else:
                return HttpResponse("success")   
        else:
            return HttpResponse("success")
    else:
        return HttpResponse("")
