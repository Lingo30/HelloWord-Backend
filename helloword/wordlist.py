from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json

from helloword.models import Word,UserInfo,FileInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem

Mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def get_wordList_from_file(request):
    print("hello")
    response = {}
    response['state'] = False

    try:
        fileInfo = FileInfo(file_info=request.FILES.get('file'))
        fileInfo.save()
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
def get_official_wordlists(request):
    response = {}
    response['state'] = False

    try:

        study_list = WordList.objects.all()

        ret = []
        for k in study_list:
            cur = {
                'listId': k.id,
                'name': k.list_name,
                'creator':k.list_author_name,
                'num': WordListItem.objects.filter(word_list_id_id=k).count()
            }
            ret.append(cur)


        response['lists'] = ret
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_user_wordlists(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('userId')

    try:
        user = UserInfo.objects.get(id=user_id)

        study_list = UserStudyList.objects.filter(user_id_id=user).values_list('id', flat=True)

        response['ids'] = list(study_list)
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_wordlist_info(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    listId = data.get('listId')

    try:
        study_list = UserStudyList.objects.get(id=listId)

        response['name'] = study_list.list_name
        response['num'] = UserStudyListItem.objects.filter(user_study_list_id_id = study_list).count()
        response['creator'] = 'TODO'
        date = str(study_list.last_study_date)
        response['date'] = {'month':Mon[int(date[5:7])-1],'day':date[8:10]}

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_words_info(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    listId = data.get('listId')
    pageSize = data.get('pageSize')
    curPage = data.get('curPage')

    try:
        study_list = UserStudyList.objects.get(id=listId)

        worditems = UserStudyListItem.objects.filter(user_study_list_id_id = study_list).order_by('id')
        ret=[]
        k = pageSize*(curPage+1)
        k = worditems.count() if k > worditems.count() else k
        for i in worditems[pageSize*curPage:k]:
            fetchword = i.word_id

            cur = {
                'wordId': fetchword.id,
                'word': fetchword.word,
                'symbol': fetchword.phonetic_symbol,
                'meaning': fetchword.definition_cn
            }
            ret.append(cur)
        response['words']=ret
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def edit_wordlists(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    deleteLists = data.get('deleteLists')
    updateLists = data.get('updateLists')

    try:
        # delete
        for k in deleteLists:
            study_list = UserStudyList.objects.get(id=k)
            study_list.delete()

        # update
        for k in updateLists:
            kid=k['listId']
            if kid not in deleteLists:
                study_list = UserStudyList.objects.get(id=kid)
                study_list.list_name=k['name']
                study_list.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_wordlists(request):
    response = {}
    response['state'] = False

    try:

        public_list = WordList.objects.values_list('id', flat=True)

        response['ids'] = list(public_list)
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def update_learn_wordlist(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    study_list_id = data.get('listId')
    user_id = data.get('userId')

    try:
        study_list = UserStudyList.objects.get(id=study_list_id)
        user_obj = UserInfo.objects.get(id=user_id)
        user_obj.last_study_list=study_list
        study_list.save()
        user_obj.save()

        response['last_study_list'] = study_list.list_name
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def add_wordlist_from_official(request):

    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8'))
    public_id = data.get('listId')
    user_id = data.get('userId')
    # TODO 根据官方词单创建，用户输入名字？
    # study_list_name = data.get('study_list_name')

    try:
        user = UserInfo.objects.get(id=user_id)
        public = WordList.objects.get(id=public_id)

        # TODO 官方词单创建使用官方名
        # TODO 一个官方词单创建几次；至多多少词单
        study_list_name = public.list_name


        to_add = UserStudyList(
            user_id=user,
            list_name = study_list_name
        )
        to_add.save()


        words = WordListItem.objects.filter(word_list_id_id=public)
        for i in words:
            add_to_list = UserStudyListItem(
                user_study_list_id=UserStudyList.objects.get(id=to_add.id),
                #user_study_list_id=UserStudyList.objects.get(id=1),
                word_id = i.word_id
            )
            add_to_list.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)
