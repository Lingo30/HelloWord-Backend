from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
from helloword.models import Word,UserInfo,Example,WordExample,WordRelation,FileInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem,UserStudyWordInfo
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
        k=data.get('user_info')
        user = UserInfo.objects.get(id=data.get('user_id'))
        user.not_unique_name = k['name']
        user.tags = ' '.join(k['tags'])
        user.save()

        response['state']=True
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
                    'wordNum': userInfo[0].daily_words_count,
                    'selectWordlist': userInfo[0].last_study_list.id
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
    #email_addr = data.get('email_addr')
    if newname == '':
        response['msg'] = '用户名不能为空'

    try:
        userInfo = UserInfo.objects.filter(username=newname)
        if userInfo.count() == 0:

            userInfo = UserInfo(username=data.get('name'),
                                password_hash=data.get('password'))
            userInfo.save()
            response['state'] = True


        else:
            response['msg'] = '用户名重复'
            return JsonResponse(response)

        to_add = UserStudyList(
            user_id=userInfo,
            list_name='新用户词单'
        )
        to_add.save()

        public = WordList.objects.get(id=1)
        words = WordListItem.objects.filter(word_list_id_id=public)
        for i in words:
            add_to_list = UserStudyListItem(
                user_study_list_id=to_add,
                word_id=i.word_id
            )
            add_to_list.save()

        userInfo.last_study_list = to_add
        userInfo.save()
        response['data'] = {
            'uid': userInfo.id,
            'wordNum': userInfo.daily_words_count,
            'selectWordlist': userInfo.last_study_list.id
        }

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
    response['tags'] = ['演讲', '运动', '旅行']
    return JsonResponse(response)


def get_user_info(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    user_id = data.get('user_id')
    user = UserInfo.objects.get(id=user_id)

    try:
        response['info'] = {
            'avatar_path': 'http://' + str(ENV['HOST']) + ':9001/static/' + str(user.user_avatar),
            'email': user.email if user.email else '',
            'words': UserStudyWordInfo.objects.filter(user_id_id=user).count(),
            'name': user.not_unique_name if user.not_unique_name else '',
            'days': user.study_days_count if user.study_days_count else 0,
            'lists': UserStudyList.objects.filter(user_id_id=user,has_done=True).count(),
            'tags': user.tags.split(" ")
        }
        response['state'] = True


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)