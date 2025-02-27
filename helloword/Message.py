from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import re
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo,PublicListCheck
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem,UserMessage,BroadcastMessage
from helloword.userInfo import checkCookie, wrapRes, wrapNewRes

def get_messages(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_find = UserInfo.objects.filter(id=user_id)
        if user_find.count() == 0:
            response['msg'] = '用户id不存在'
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        ret = []
        pattern = r'\..{6}'
        for i in UserMessage.objects.filter(user_id_id=user_obj).order_by('-post_time'):
            type='【通知】'
            find_type = re.findall(r"[【].*?[】]", i.message)
            if len(find_type)>0:
                if find_type[0]!="【1】":
                    type=find_type[0]
                else:
                    type = '【平台更新公告】'

            cur = {
                'id': i.id,
                'title': type,
                'content': i.message,
                'state':i.has_read,
                'time':re.sub(pattern,"",str(i.post_time).replace('T', ' ')),
            }
            ret.append(cur)

        response['messages'] = ret
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def set_message_state(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')
        message_id = data.get('messageId')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_find = UserInfo.objects.filter(id=user_id)
        if user_find.count() == 0:
            response['msg'] = '用户id不存在'
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        msg_find = UserMessage.objects.filter(id=message_id,user_id_id=user_obj)
        if msg_find.count() == 0:
            response['msg'] = '消息不存在或者与用户信息不匹配'
            return JsonResponse(response)
        msg_obj = UserMessage.objects.get(id=message_id,user_id_id=user_obj)

        msg_obj.has_read=True
        msg_obj.save()

        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def send_message_to_user(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')
        admin_id = data.get('adminId')
        message = data.get('message')
        title = data.get('title')
        if title=="":
            title='Re: Bug反馈'

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        user_find = UserInfo.objects.filter(id=user_id)
        if user_find.count() == 0:
            response['msg'] = '用户id不存在'
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        message_obj = UserMessage(user_id=user_obj,message='【'+title+'】'+message)
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

        message_obj = BroadcastMessage(message='【公告】'+message)
        message_obj.save()

        user_all = UserInfo.objects.all()
        for k in user_all:
            message_obj = UserMessage(user_id=k, message='【平台公告】'+message)
            message_obj.save()

        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)