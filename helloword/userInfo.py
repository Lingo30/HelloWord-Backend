from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import UserInfo, FileInfo
from pathlib import Path
import sys
import os

with open('env.json') as env:
    ENV = json.load(env)


def copy(src_file, dst_file):
    '''  src_file : 源文件名
         dst_file : 目标文件名
         返回值: True成功, False 失败
    '''
    try:
        fr = open(src_file, 'rb')
        try:
            fw = open(dst_file, 'wb')
            try:
                while True:
                    b = fr.read(4096)
                    if not b:
                        break
                    fw.write(b)
            finally:
                fw.close()
        finally:
            fr.close()
    except OSError as e:
        print(str(e))
        return False
    return True


def submit_info(request):
    response = {}
    response['state'] = False

    try:

        data = json.loads(request.body.decode())
        print(data.get('user_info'))

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def submit_image(request):
    print("hello")
    response = {}
    response['state'] = False

    iid = int(str(request.FILES.get('user_id').read())[2:-1])
    print(iid)

    try:
        file = request.FILES.get('img')
        #newfile = FileInfo(file_info=file)
        #newfile.save()
        user_obj = UserInfo.objects.get(id=iid)
        user_obj.user_avatar=file
        user_obj.save()

        src = 'media/' + str(user_obj.user_avatar)
        dst = '../backend_static/' + str(user_obj.user_avatar)
        if copy(src, dst):
            print("复制文件成功!")
        else:
            print("复制文件失败!")
            response['msg'] = "复制文件失败!"

        response['url'] = 'http://' + str(ENV['HOST']) + ':9001/static/' + str(user_obj.user_avatar)



        response['state'] = True


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


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


def change_pwd(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    user_id = data.get('user_id')
    old_pwd = data.get('old_pwd')
    new_pwd = data.get('new_pwd')

    try:
        user = UserInfo.objects.get(id=user_id)

        if user.password_hash == old_pwd:
            user.password_hash = new_pwd
            user.save()
            response['state'] = True

        else:
            response['msg'] = '原密码错误'

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


ENV = {}
with open('env.json') as env:
    ENV = json.load(env)


def get_recommend_tags(request):
    response = {}
    response['tags'] = ['test1', 'test2']
    return JsonResponse(response)


def get_user_info(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    user_id = data.get('user_id')

    try:
        response['info'] = {
            'avatar_path': 'http://' + str(ENV['HOST']) + ':9001/static/admin/img/search.svg',
            'email': 'email',
            'words': 100,
            'name': 'name',
            'days': 100,
            'lists': 100,
            'tags': ['11', '22']
        }
        response['state'] = True


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)