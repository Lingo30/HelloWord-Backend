from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import Word,UserInfo,Feedback

def add_feedback(request):
    response = {}
    response['state'] = False


    try:
        data = json.loads(request.body.decode())

        user = UserInfo.objects.get(id=data.get('userId'))
        type = data.get('type')
        modules = data.get('modules')
        content = data.get('content')

        feedback = Feedback(user_id=user,
                            type = type,
                            modules = ' '.join(modules),
                            content = content)
        feedback.save()


        response['state']=True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)