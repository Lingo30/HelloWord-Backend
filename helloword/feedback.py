from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,Feedback
from helloword.userInfo import checkCookie, wrapRes


def add_feedback(request):
    response = {}
    response['state'] = False


    try:
        data = json.loads(request.body.decode())
        user_id=data.get('userId')
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user = UserInfo.objects.get(id=user_id)
        type = data.get('type')
        modules = data.get('modules')
        content = data.get('content')

        today_feedback = Feedback.objects.filter(user_id=user,post_time__gte=datetime.date.today())
        print(datetime.date.today()-datetime.timedelta(days=1))
        if today_feedback.count()>3:
            response['msg'] = '今天的反馈已经收到啦~明天再来吧'
            return JsonResponse(response)

        feedback = Feedback(user_id=user,
                            type = type,
                            modules = ' '.join(modules),
                            content = content)
        feedback.save()


        response['state']=True
        return wrapRes(response, user_id)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)