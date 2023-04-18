from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import ChatHistory
from helloword.models import UserInfo
from chatgpt import client
from chatgpt.tools import chat

def user_send(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    question = data.get('question')

    try:
        user_chat = ChatHistory(user_id_id=user_id, message=question, type=True)
        user_chat.save()
        messages = chat.chat(question)
        gpt_respond = client.Clinet().send_message(messages)
        gpt_chat = ChatHistory(user_id_id=user_id, message=gpt_respond, type=False)
        gpt_chat.save()
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
        log_history = ChatHistory.objects.filter(user_id_id=user_id)
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
