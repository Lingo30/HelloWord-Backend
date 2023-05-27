from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo,PublicListCheck
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem
from helloword.userInfo import checkCookie, wrapRes, wrapNewRes
from helloword.models import WordsStory,WordsCloze,WritingHistory,ReadingHistory

Mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def get_record_info(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        record_id = data.get('record_id')
        recd_type = data.get('type')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)

        if recd_type == 0:
            # write
            recd_obj = WritingHistory.objects.get(id=record_id,user_id = user_obj)
            raw = recd_obj.input
            response['content'] = raw
            date = str(recd_obj.post_time)
            response['date'] = {'month': Mon[int(date[5:7]) - 1], 'day': date[8:10]}

            response['state'] = True
            return wrapRes(response, user_id)
        elif recd_type == 1:
            # story
            recd_obj = WordsStory.objects.get(id=record_id,user_id = user_obj)
            raw = recd_obj.story
            response['content'] = raw
            date = str(recd_obj.post_time)
            response['date'] = {'month': Mon[int(date[5:7]) - 1], 'day': date[8:10]}

            response['state'] = True
            return wrapRes(response, user_id)
        elif recd_type == 2:
            # cloze
            recd_obj = WordsCloze.objects.get(id=record_id,user_id = user_obj)
            raw = recd_obj.cloze
            # todo 替换逻辑
            response['content'] = raw
            date = str(recd_obj.post_time)
            response['date'] = {'month': Mon[int(date[5:7]) - 1], 'day': date[8:10]}

            response['state'] = True
            return wrapRes(response, user_id)
        else :
            response['msg'] = '类型不存在'
            return JsonResponse(response)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_history_record_id(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        recd_type = data.get('type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)
        start_obj = datetime.datetime(year=int(start_date['year']), month=int(start_date['month']), day=int(start_date['day']), hour=0, minute=0, second=0)
        end_obj = datetime.datetime(year=int(end_date['year']), month=int(end_date['month']), day=int(end_date['day']), hour=23, minute=59, second=59)
        if (start_obj > end_obj):
            response['msg'] = '起始时间小于结束时间'
            return JsonResponse(response)

        if recd_type == 0:
            # write
            recd_obj = WritingHistory.objects.filter(user_id = user_obj,post_time__range=(start_obj,end_obj)).exclude(output__isnull=True)
            response['ids'] = list(recd_obj.values_list('id', flat=True))
            response['state'] = True
            return wrapRes(response, user_id)
        elif recd_type == 1:
            # story
            recd_obj = WordsStory.objects.filter(user_id=user_obj, post_time__range=(start_obj, end_obj)).exclude(story__isnull=True)
            response['ids'] = list(recd_obj.values_list('id', flat=True))
            response['state'] = True
            return wrapRes(response, user_id)
        elif recd_type == 2:
            # cloze
            recd_obj = WordsCloze.objects.filter(user_id=user_obj, post_time__range=(start_obj, end_obj)).exclude(cloze__isnull=True)
            response['ids'] = list(recd_obj.values_list('id', flat=True))
            response['state'] = True
            return wrapRes(response, user_id)
        else :
            response['msg'] = '类型不存在'
            return JsonResponse(response)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_story_record(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        record_id = data.get('record_id')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        recd_obj = WordsStory.objects.get(id=record_id,user_id=user_id)
        response['content']=recd_obj.story
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_blank_record(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        record_id = data.get('record_id')

        if not checkCookie(request, response, user_id):
            return JsonResponse(response)

        recd_obj = WordsCloze.objects.get(id=record_id, user_id=user_id)

        response['content'] = recd_obj.cloze
        response['answer'] = recd_obj.answers.split(' ')
        response['originWords'] = recd_obj.words.split(' ')
        raw = recd_obj.eordlist.split(' ')
        wordlist=[]
        for i in range(0,len(raw),2): #从下标为0的元素开始
            cur = {
                'start': int(raw[i]),
                'end': int(raw[i+1])
            }
            wordlist.append(cur)

        response['wordList'] = wordlist
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_writing_record(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        record_id = data.get('record_id')

        if not checkCookie(request, response, user_id):
            return JsonResponse(response)

        recd_obj = WritingHistory.objects.get(id=record_id, user_id=user_id)
        response['article'] = recd_obj.input
        response['comment'] = json.loads(recd_obj.output)
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
