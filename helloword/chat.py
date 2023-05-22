from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import ChatHistory
from helloword.models import UserInfo
from chatgpt import client
from chatgpt.tools import chat
import datetime
import re

from helloword.userInfo import checkCookie, wrapRes
from helloword.preload import tts
dailly_times = 7
def user_send(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    question = data.get('question')

    try:
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        if user_obj.gpt_lock and user_obj.gpt_lock != "":
            response['msg'] = '小助手正在为您服务，请等待结果返回~'
            return JsonResponse(response)
        user_obj.gpt_lock = 'sentence'
        user_obj.save()

        user_chat = ChatHistory(user_id=user_obj, message=question, type=True)

        times_left = dailly_times - ChatHistory.objects.filter(user_id_id=user_obj,
                                                               type=True,
                                                              post_time__gte=datetime.date.today()).count()
        if times_left == 0:
            response['last_times'] = 0
            response['msg'] = '今天的对话次数已经用完啦！明天再来吧'
            user_obj.gpt_lock = ""
            user_obj.save()
            return JsonResponse(response)


        user_chat.save()

        messages = chat.chat(question)
        gpt_respond = client.Client().send_message(messages)


        gpt_chat = ChatHistory(user_id=user_obj, message=gpt_respond, type=False)
        gpt_chat.save()

        times_left -= 1
        response['msg'] = '今日剩余次数：' + str(times_left)
        response['last_times'] = times_left


        response['receive_time'] = user_chat.post_time
        response['post_message'] = gpt_respond
        response['post_time'] = gpt_chat.post_time

        response['state'] = True
        user_obj.gpt_lock = ""
        user_obj.save()
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    try:
        user_obj = UserInfo.objects.get(id=user_id)
        user_obj.gpt_lock = ""
        user_obj.save()
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_log_history(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    try:
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user_obj=UserInfo.objects.get(id=user_id)
        log_history = ChatHistory.objects.filter(user_id_id=user_obj)
        history = []
        pattern = r'\..{6}'
        for item in log_history:
            cur = {
                'type' : item.type,
                'time' : re.sub(pattern,"",str(item.post_time).replace('T', ' ')),
                'content' : item.message
            }
            history.append(cur)
        response['history'] = history
        response['state'] = True
        return wrapRes(response, user_id)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
