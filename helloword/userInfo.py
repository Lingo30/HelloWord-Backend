from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,Example,WordExample,WordRelation,FileInfo,EmailToken,EmailResetToken
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem,UserStudyWordInfo,DailyNum
from pathlib import Path
import sys
import os
import struct
import random
import json
from captcha.image import ImageCaptcha
import random
import string

with open('env.json') as env:
    ENV = json.load(env)

token_msg='token失效，请重新登录'

def wrapNewRes(response,user_id):
    try:
        cookie_res = JsonResponse(response)
        cookie_token = gen_token()
        userInfo=UserInfo.objects.get(id=user_id)
        userInfo.cookie_token = cookie_token
        userInfo.save()
        cookie_res.set_cookie(key='user_token', value=cookie_token,
                              expires=datetime.datetime.now() + datetime.timedelta(days=2),samesite=None,
                              secure=True, httponly=True)
        return cookie_res
    except Exception as e:
        print(str(e))
        response['state']=False
        response['msg']=str(e)
        return JsonResponse(response)
def wrapRes(response,user_id):
    try:
        cookie_res = JsonResponse(response)
        #cookie_token = gen_token()
        userInfo=UserInfo.objects.get(id=user_id)
        #userInfo.cookie_token = cookie_token
        #userInfo.save()
        cookie_res.set_cookie(key='user_token', value=userInfo.cookie_token,
                              expires=datetime.datetime.now() + datetime.timedelta(days=2),samesite=None,
                              secure=True, httponly=True)
        return cookie_res
    except Exception as e:
        print(str(e))
        response['state']=False
        response['msg']=str(e)
        return JsonResponse(response)

def checkCookie(request,response,user_id):
    try:
        cookie = request.COOKIES['user_token']

        if not cookie or cookie == '':
            response['msg'] = token_msg
            response['state'] = False
            return False
        userInfo = UserInfo.objects.filter(id=user_id, cookie_token=cookie)
        if userInfo.count() == 0:
            response['msg'] = token_msg
            response['state'] = False
            return False
        return True
    except Exception as e:
        print(str(e))
        response['state']=False
        response['msg']=token_msg
        return False


type_dict = {
    'FFD8FF': 'jpg',
    '89504E47': 'png',
}
max_len = len(max(type_dict, key=len)) // 2

def get_size(fobj):
    try:
        if fobj.content_length:
            return fobj.content_length
    except Exception as e:
        print(str(e))

    try:
        pos = fobj.tell()
        fobj.seek(0, 2)  #seek to end
        size = fobj.tell()
        fobj.seek(pos)  # back to original position
        return size
    except Exception as e:
        print(str(e))
def get_filetype(file):
    # 读取二进制文件开头一定的长度
    try:
        filetype = file.name.split('.')[-1]
        if filetype != 'jpg' and filetype != 'png':
            return False

        byte = file.read(max_len)
        # 解析为元组
        byte_list = struct.unpack('B' * max_len, byte)
    except Exception as e:
        print(str(e))
        return False
    # 转为16进制
    code = ''.join([('%X' % each).zfill(2) for each in byte_list])
    # 根据标识符筛选判断文件格式
    result = list(filter(lambda x: code.startswith(x), type_dict))
    print(code)
    if result:
        return True
    else:
        return False

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
        user_id=data.get('user_id')
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        k=data.get('user_info')
        user = UserInfo.objects.get(id=user_id)
        user.not_unique_name = k['name']
        user.tags = ' '.join(list(set(k['tags'])))
        user.save()

        response['state']=True
        return wrapRes(response,user_id)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def submit_image(request):
    response = {}
    response['state'] = False

    try:
        str_tmp = str(request.FILES.get('user_id').read())[2:-1].replace("\"", "")
        print(str_tmp)
        iid = int(str_tmp)
        #iid = int(str(request.FILES.get('user_id').read())[2:-1])
        if not checkCookie(request,response,iid):
            return JsonResponse(response)
        file = request.FILES.get('img')

        if not get_filetype(file):
            response['state'] = True
            response['msg'] = '请上传jpg或png文件'
            return JsonResponse(response)

        if get_size(file)>4000000:
            response['state'] = True
            response['msg'] = '图片超过4MB'
            return JsonResponse(response)


        user_obj = UserInfo.objects.get(id=iid)

        old_src = 'media/' + str(user_obj.user_avatar)
        old_dst = '../backend_static/' + str(user_obj.user_avatar)

        user_obj.user_avatar=file
        user_obj.save()

        src = 'media/' + str(user_obj.user_avatar)
        dst = '../backend_static/' + str(user_obj.user_avatar)
        if copy(src, dst):
            print("复制文件成功!")
        else:
            print("复制文件失败!")
            response['msg'] = "图片上传失败!"
            return JsonResponse(response)

        try:
            if str(user_obj.user_avatar)!="user_avatar/default_avatar.jpg":
                os.remove(old_src)
                os.remove(old_dst)

        except Exception as e:
            print(str(e))

        response['url'] = 'http://' + str(ENV['HOST']) +  str(ENV['API'])  +'/static/' + str(user_obj.user_avatar)
        response['state'] = True
        return wrapRes(response,iid)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def gen_token():
    # 返回一个随机字符串，生成4位验证码
    return ''.join(random.choices('0123456789abcdefghigklmnopqrstuvwxyz', k=24))

def gen_num_token():
    # 返回一个随机字符串，生成4位验证码
    return ''.join(random.choices('0123456789abcdefghigklmnopqrstuvwxyz', k=6))

dataKV=[]
codeMap = {}
with open('../outputKV.json') as jsonKV:
    dataKV = json.load(jsonKV)
    for i in dataKV:
        codeMap[i['key']]=i['value']


def modify_KVcode(key):
    #print(dataKV)
    #key = 'TNEK'
    new = ''.join(random.choices('ABDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    num = 0
    for i in dataKV:
        if i['key'] == key:
            print(i)
            num = int(i['id']) - 1
            i['value'] = new
            break

    codeMap[key] = new
    characters = string.digits + string.ascii_uppercase
    width, height, n_len, n_class = 160, 50, 4, len(characters)
    generator = ImageCaptcha(width=width, height=height)
    img = generator.generate_image(new)

    #file_name = './test1/' + str(num).zfill(5) + '_' + key + '.jpg'
    file_name = '../backend_static/checkcode/' + str(num).zfill(5) + '_' + key + '.jpg'
    img.save(file_name)
    #print(dataKV)
    for i in dataKV:
        if i['key'] == key:
            print(i)
    with open("../outputKV.json", "w") as json_file:
        json.dump(dataKV, json_file, ensure_ascii=False, indent=4)

def get_verify_img(request):
    response = {}
    response['state'] = False
    try:
        k = random.randint(1,200)
        codekey = dataKV[k-1]['key']
        img_url = 'http://' + str(ENV['HOST']) + str(ENV['API']) +'/static/checkcode/'+ str(k-1).zfill(5) +'_' + codekey +  '.jpg'
        response['img'] = img_url
        response['imgCode'] = codekey
        response['state'] = True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def logout(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')
        if not checkCookie(request, response, user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)
        user_obj.cookie_token=''
        user_obj.save()
        response['state'] = True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)



def get_vip_info(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        if not checkCookie(request, response, user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)
        response['day_num']=user_obj.month_login

        response['word_num'] = 0
        today_study = DailyNum.objects.filter(user_id_id=user_obj,post_time=datetime.datetime.today())
        if today_study.count()!=0:
            response['word_num']=today_study[0].num

        response['friend_num']=user_obj.has_invite

        if not user_obj.invite_code:
            code = gen_num_token()
            barrier = 0
            while UserInfo.objects.filter(invite_code=code).count()!=0:
                barrier+=1
                code = gen_num_token()
                if barrier>10:
                    response['msg'] = '邀请码生成错误，请重试'
                    return JsonResponse(response)
            user_obj.invite_code = code
            user_obj.save()

        response['invite_code']=user_obj.invite_code
        response['state']=True

        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def change_custom(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')
    user_custom = data.get('user_custom')

    try:
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)
        user_obj.custom = user_custom
        user_obj.save()
        response['state'] = True
        return wrapRes(response, user_id)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def login(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    print(data)
    try:
        value = data.get('verify')
        key = data.get('imgCode')

        if value=="":
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        if codeMap.get(key,'').lower() != str(value).lower():
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        userInfo = UserInfo.objects.filter(username=data.get('name'))
        if userInfo.count() == 0:
            response['msg'] = '用户名不存在'

        elif userInfo.count() == 1:
            if userInfo[0].password_hash == data.get('password'):
                response['state'] = True
                response['data'] = {
                    'uid': userInfo[0].id,
                    'wordNum': userInfo[0].daily_words_count,
                    'selectWordlist': userInfo[0].last_study_list.id,
                    'custom': userInfo[0].custom
                }

                user_obj = userInfo[0]
                if not user_obj.last_login_date:
                    user_obj.month_login = 1
                    user_obj.save()
                elif user_obj.last_login_date != datetime.date.today():
                    if datetime.datetime.today().month != user_obj.last_login_date.month:
                        user_obj.month_login = 1
                    else:
                        user_obj.month_login = user_obj.month_login + 1
                        if user_obj.month_login == 10:
                            if (not user_obj.vip_time) or user_obj.vip_time < datetime.datetime.now():
                                user_obj.vip_time = datetime.datetime.now() + datetime.timedelta(days=7)
                            else:
                                user_obj.vip_time = user_obj.vip_time + datetime.timedelta(days=7)
                    user_obj.save()
                modify_KVcode(key)
                return wrapNewRes(response, userInfo[0].id)

            else:
                response['msg'] = '密码错误'

        else:
            response['msg'] = '登录用户名重复，请联系平台管理员'

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def adminLogin(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    print(data)
    try:
        value = data.get('verify')
        key = data.get('imgCode')

        if value=="":
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        if codeMap.get(key,'').lower() != str(value).lower():
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        userInfo = UserInfo.objects.filter(username=data.get('name'))
        if userInfo.count() == 0:
            response['msg'] = '用户名不存在'

        elif userInfo.count() == 1:
            if userInfo[0].password_hash == data.get('password'):
                if userInfo[0].user_type and userInfo[0].user_type == 'admin':

                    response['state'] = True
                    response['data'] = {
                        'uid': userInfo[0].id,
                        'wordNum': userInfo[0].daily_words_count,
                        'selectWordlist': userInfo[0].last_study_list.id,
                        'custom': userInfo[0].custom
                    }

                    user_obj = userInfo[0]
                    if not user_obj.last_login_date:
                        user_obj.month_login = 1
                        user_obj.save()
                    elif user_obj.last_login_date != datetime.date.today():
                        if datetime.datetime.today().month != user_obj.last_login_date.month:
                            user_obj.month_login = 1
                        else:
                            user_obj.month_login = user_obj.month_login + 1
                            if user_obj.month_login == 10:
                                if (not user_obj.vip_time) or user_obj.vip_time < datetime.datetime.now():
                                    user_obj.vip_time = datetime.datetime.now() + datetime.timedelta(days=7)
                                else:
                                    user_obj.vip_time = user_obj.vip_time + datetime.timedelta(days=7)
                        user_obj.save()

                    return wrapNewRes(response, userInfo[0].id)
                else:
                    response['msg'] = '没有管理员权限'
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
        value = data.get('verify')
        key = data.get('imgCode')

        if value=="":
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        if codeMap.get(key,'').lower() != str(value).lower():
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        email_addr = data.get('email')
        code = data.get('code')

        t = EmailToken.objects.filter(email_addr=email_addr, token=code)
        if t.count() != 0:

            email_token = t[0]
            if email_token.has_register:
                response['msg'] = '该邮箱已注册'
                return JsonResponse(response)

            if datetime.datetime.now() - email_token.gen_time > datetime.timedelta(minutes=20):
                response['msg'] = '注册码已失效，请重试'
                return JsonResponse(response)

        else:
            response['msg'] = '邮箱验证码错误'
            return JsonResponse(response)

        userInfo = UserInfo.objects.filter(username=newname)
        if userInfo.count() != 0:
            response['msg'] = '用户名重复'
            return JsonResponse(response)

        invite_code = data.get('invite_code')
        if invite_code != "":
            invite_user_find = UserInfo.objects.filter(invite_code=invite_code)
            if invite_user_find.count()==0:
                response['msg'] = '邀请码不存在'
                return JsonResponse(response)
            else:
                invite_user_obj = invite_user_find[0]
                invite_user_obj.has_invite=invite_user_obj.has_invite+1

                if (not invite_user_obj.vip_time) or invite_user_obj.vip_time < datetime.datetime.now():
                    invite_user_obj.vip_time = datetime.datetime.now() + datetime.timedelta(days=3)
                else:
                    invite_user_obj.vip_time = invite_user_obj.vip_time + datetime.timedelta(days=3)

                invite_user_obj.save()


        userInfo = UserInfo(username=data.get('name'),
                            email=email_addr,
                            password_hash=data.get('password'))

        userInfo.save()

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
            'selectWordlist': userInfo.last_study_list.id,
            'custom': userInfo.custom
        }

        email_token.has_register = True
        email_token.save()

        userInfo.month_login = 1
        userInfo.save()

        response['state'] = True
        modify_KVcode(key)

        return wrapNewRes(response,userInfo.id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def reset_password(request):
    response = {}
    response['state'] = False
    try:
        data = json.loads(request.body.decode())

        newname = data.get('name')
        if newname == '':
            response['msg'] = '用户名不能为空'

        value = data.get('verify')
        key = data.get('imgCode')

        if value=="":
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        if codeMap.get(key, '').lower() != str(value).lower():
            response['msg'] = '验证码错误'
            return JsonResponse(response)

        email_addr = data.get('email')
        code = data.get('code')

        has_user = UserInfo.objects.filter(username=newname)
        if has_user.count() == 0:
            response['msg'] = '用户名不存在'
            return JsonResponse(response)
        elif has_user[0].email != email_addr:
            response['msg'] = '输入邮箱与用户名不匹配'
            return JsonResponse(response)

        t = EmailResetToken.objects.filter(email=email_addr, token=code)
        if t.count() != 0:
            email_token=t[0]
            if datetime.datetime.now() - email_token.gen_time > datetime.timedelta(minutes=20):
                response['msg'] = '注册码已失效，请重试'
                return JsonResponse(response)

        else:
            response['msg'] = '邮箱验证码错误'
            return JsonResponse(response)

        userInfo = UserInfo.objects.get(username=newname)
        userInfo.password_hash=data.get('password')
        userInfo.save()
        response['state'] = True


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def cookie_login(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    user_id = data.get('userId')

    try:
        userInfo = UserInfo.objects.get(id=user_id)
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        else:
            response['state'] = True
            response['data'] = {
                'uid': userInfo.id,
                'wordNum': userInfo.daily_words_count,
                'selectWordlist': userInfo.last_study_list.id,
                'custom': userInfo.custom
            }

            print("user_id: "+str(userInfo.id)+" username: "+str(userInfo.username))

            user_obj = userInfo
            if not user_obj.last_login_date:
                user_obj.month_login = 1
                user_obj.save()
            elif user_obj.last_login_date != datetime.date.today():
                if datetime.datetime.today().month != user_obj.last_login_date.month:
                    user_obj.month_login = 1
                else:
                    user_obj.month_login = user_obj.month_login + 1
                    if user_obj.month_login==10:
                        if (not user_obj.vip_time) or user_obj.vip_time<datetime.datetime.now():
                            user_obj.vip_time=datetime.datetime.now()+datetime.timedelta(days=7)
                        else:
                            user_obj.vip_time=user_obj.vip_time+datetime.timedelta(days=7)
                user_obj.save()

            return wrapNewRes(response,user_id)

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
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user = UserInfo.objects.get(id=user_id)

        if user.password_hash == old_pwd:
            user.password_hash = new_pwd
            user.save()
            response['state'] = True
            return wrapNewRes(response, user_id)

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
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_obj = user
        if not user_obj.last_login_date:
            user_obj.month_login = 1
            user_obj.save()
        elif user_obj.last_login_date != datetime.date.today():
            if datetime.datetime.today().month != user_obj.last_login_date.month:
                user_obj.month_login = 1
            else:
                user_obj.month_login = user_obj.month_login + 1
                if user_obj.month_login == 10:
                    if (not user_obj.vip_time) or user_obj.vip_time < datetime.datetime.now():
                        user_obj.vip_time = datetime.datetime.now() + datetime.timedelta(days=7)
                    else:
                        user_obj.vip_time = user_obj.vip_time + datetime.timedelta(days=7)
            user_obj.save()

        cal_vip_second = 0
        if user.vip_time and user.vip_time > datetime.datetime.now():
            cal_vip_second = (user.vip_time-datetime.datetime.now()).total_seconds()

        response['info'] = {
            'avatar_path': 'http://' + str(ENV['HOST']) + str(ENV['API']) +'/static/' + str(user.user_avatar),
            'email': user.email if user.email else '',
            'words': UserStudyWordInfo.objects.filter(user_id_id=user).count(),
            'name': user.not_unique_name if user.not_unique_name else '',
            'days': user.month_login if user.month_login else 0,
            'lists': UserStudyList.objects.filter(user_id_id=user,has_done=True).count(),
            'tags': user.tags.split(" "),
            'last_time': cal_vip_second
        }
        response['state'] = True
        return wrapRes(response, user_id)


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)