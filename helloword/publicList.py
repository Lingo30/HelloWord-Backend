from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo,PublicListCheck
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem
from helloword.userInfo import checkCookie, wrapRes, wrapNewRes


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
        list_obj = WordList.objects.get(id=list_id)
        if PublicListCheck.objects.filter(user_id=user_obj,list_id=list_obj).count() == 0:
            new_submit = PublicListCheck(user_id=user_obj,list_id=list_obj)
            new_submit.save()

            response['state'] = True
            return wrapRes(response, user_id)
        else :
            response['msg'] = '该词单已提交审核中'
            return JsonResponse(response)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)