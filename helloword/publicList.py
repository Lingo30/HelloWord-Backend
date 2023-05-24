from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo,PublicListCheck,UserMessage
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem
from helloword.userInfo import checkCookie, wrapRes, wrapNewRes


def get_user_submit_wordlists(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        admin_id = data.get('adminId')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        ret = []
        for i in PublicListCheck.objects.exclude(user_study_list_id__isnull=True):
            handleState = 0
            if i.check_status=='accept':
                handleState = 1
            elif i.check_status=='reject':
                handleState = 2
            cur = {
                'listId': i.user_study_list_id.id,
                'listName': i.user_study_list_id.list_name,
                'userId': i.user_id.id,
                'handleState': handleState,
                'handleMessage': i.send_message.message if i.send_message else ""
            }
            ret.append(cur)

        response['messages'] = ret

        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def accept_submit_wordlist(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        admin_id = data.get('adminId')
        list_id = data.get('listId')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        list_obj = UserStudyList.objects.get(id=list_id)
        check_find = PublicListCheck.objects.filter(list_id=list_obj, check_status='user_submit')
        if check_find.count() == 0:
            response['msg'] = '未上传该词单'
            return JsonResponse(response)
        elif check_find.count() > 1:
            response['msg'] = '多次上传相同词单，请联系管理员处理'
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=list_obj.list_author.id)
        send_message='【词单审核通知】您的词单《' + list_obj.list_name + '》已成功发布至官方词单~'
        message_obj = UserMessage(user_id=user_obj, message=send_message)
        message_obj.save()

        check_obj = check_find[0]
        check_obj.check_status = 'accept'
        check_obj.send_message = message_obj
        check_obj.save()

        list_obj.create_type = 'official'
        list_obj.save()

        to_add = WordList(
            list_name=list_obj.list_name,
            list_author_name=list_obj.list_author.username,
            list_author=list_obj.list_author,
            gen_type='1'
        )
        to_add.save()

        words = UserStudyListItem.objects.filter(user_study_list_id_id=list_obj)
        for i in words:
            add_to_list = WordListItem(
                word_list_id=to_add,
                word_id=i.word_id
            )
            add_to_list.save()

        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def reject_submit_wordlist(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        admin_id = data.get('adminId')
        list_id = data.get('listId')
        message = data.get('message')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        list_obj = UserStudyList.objects.get(id=list_id)
        check_find = PublicListCheck.objects.filter(list_id=list_obj,check_status='user_submit')
        if check_find.count() == 0:
            response['msg'] = '未上传该词单'
            return JsonResponse(response)
        elif check_find.count()>1:
            response['msg'] = '多次上传相同词单，请联系管理员处理'
            return JsonResponse(response)

        send_message = '【词单审核通知】您的词单《' + list_obj.list_name + '》未成功发布。\n【未通过审核原因】' + message
        user_obj = UserInfo.objects.get(id=list_obj.list_author.id)
        message_obj = UserMessage(user_id=user_obj, message=send_message)
        message_obj.save()

        check_obj = check_find[0]
        check_obj.check_status = 'reject'
        check_obj.send_message = message_obj
        check_obj.save()

        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_submit_wordlist(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        admin_id = data.get('adminId')
        listId = data.get('listId')

        if not checkCookie(request,response,admin_id):
            return JsonResponse(response)

        study_list = UserStudyList.objects.get(id=listId)
        worditems = UserStudyListItem.objects.filter(user_study_list_id_id=study_list).order_by('id')
        ret = []

        for i in worditems:
            fetchword = i.word_id

            cur = {
                'wordId': fetchword.id,
                'word': fetchword.word,
                'meaning': fetchword.definition_cn.replace("\\n", "\n").replace("\\r", "")
            }
            ret.append(cur)

        response['words'] = ret
        response['state'] = True
        return wrapRes(response, admin_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def submit_official_wordlist(request):

    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('userId')
        list_id = data.get('listId')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)
        list_obj = UserStudyList.objects.get(id=list_id)
        if PublicListCheck.objects.filter(user_id=user_obj,list_id=list_obj).exclude(check_status='reject').count() == 0:
            if list_obj.list_author.id != user_id:
                response['msg'] = '词单与作者不匹配'
                return JsonResponse(response)
            new_submit = PublicListCheck(user_id=user_obj,list_id=list_obj)
            new_submit.save()

            response['state'] = True
            return wrapRes(response, user_id)
        else :
            response['msg'] = '该词单已提交审核'
            return JsonResponse(response)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)