from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import ChatHistory
from helloword.models import UserInfo
from chatgpt import client
from chatgpt.tools import chat
import datetime

dailly_times = 7
def user_send(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    question = data.get('question')

    try:
        user_obj = UserInfo.objects.get(id=user_id)

        times_left = dailly_times - ChatHistory.objects.filter(user_id_id=user_obj,
                                                               type=False,
                                                              post_time__gte=datetime.date.today()).count()
        if times_left == 0:
            response['last_times'] = 0
            response['msg'] = '今天的对话次数已经用完啦！明天再来吧'
            return JsonResponse(response)

        messages = chat.chat(question)
        gpt_respond = client.Clinet().send_message(messages)

        user_chat = ChatHistory(user_id=user_obj, message=question, type=True)
        user_chat.save()
        gpt_chat = ChatHistory(user_id=user_obj, message=gpt_respond, type=False)
        gpt_chat.save()

        times_left -= 1
        response['msg'] = '今日剩余次数：' + str(times_left)
        response['last_times'] = times_left


        response['receive_time'] = user_chat.post_time
        response['post_message'] = gpt_respond
        response['post_time'] = gpt_chat.post_time

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_log_history(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    try:
        user_obj=UserInfo.objects.get(id=user_id)
        log_history = ChatHistory.objects.filter(user_id_id=user_obj)
        history = []
        for item in log_history:
            cur = {
                'type' : item.type,
                'time' : item.post_time,
                'content' : item.message
            }
            history.append(cur)
        response['history'] = history
        response['state'] = True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
