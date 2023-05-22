from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo,PublicListCheck
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem,UserMessage,BroadcastMessage
from helloword.userInfo import checkCookie, wrapRes, wrapNewRes

def send_message_to_user(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')
        admin_id = data.get('adminId')
        message = data.get('message')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        user_find = UserInfo.objects.filter(id=user_id)
        if user_find.count() == 0:
            response['msg'] = '用户id不存在'
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        message_obj = UserMessage(user_id=user_obj,message=message)
        message_obj.save()
        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def send_to_all(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        admin_id = data.get('adminId')
        message = data.get('message')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        message_obj = BroadcastMessage(message=message)
        message_obj.save()
        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)