from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import UserInfo


def login(request):
    print("hello")
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    print(data)
    try:
        userInfo = UserInfo.objects.filter(username=data.get('name'))
        if userInfo.count() == 0:
            response['msg'] = '用户名不存在'

        elif userInfo.count() == 1:
            if userInfo[0].password_hash == data.get('password'):
                response['state'] = True
                response['data'] = {
                    'uid': userInfo[0].id,
                    'wordNum': userInfo[0].daily_words_count
                }
            else:
                response['msg'] = '密码错误'

        else:
            response['msg'] = '登录用户名重复，请联系平台管理员'

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def register(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    newname = data.get('name')
    if newname == '':
        response['msg'] = '用户名不能为空'

    try:
        userInfo = UserInfo.objects.filter(username=newname)
        if userInfo.count() == 0:
            userInfo = UserInfo(username=data.get('name'),
                                password_hash=data.get('password'))
            userInfo.save()
            response['state'] = True
            response['data'] = {
                'uid': userInfo.id,
                'wordNum': userInfo.daily_words_count
            }

        else:
            response['msg'] = '用户名重复'

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
