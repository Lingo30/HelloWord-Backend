from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json

from helloword.models import Word,UserInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem

def add_studylist_from_public(request):

    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8'))
    public_id = data.get('public_id')
    user_id = data.get('user_id')
    study_list_name = data.get('study_list_name')

    try:
        user = UserInfo.objects.get(id=user_id)
        public = WordList.objects.get(id=public_id)


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

def add_public_list(request):
    response = {}
    response['state'] = False

    try:
        words = Word.objects.all()
        list = WordList.objects.count()
        newListName = '平台词单'+str(list)

        to_add = WordList(list_name=newListName,
                      list_author_name='HelloWord团队',
                      description='测试词单',
                      gen_type='0')
        to_add.save()


        for i in words:
            add_to_list = WordListItem(
                # word_list_id=WordList.objects.get(id=1),
                word_list_id=WordList.objects.get(id=to_add.id),
                word_id = i
            )
            add_to_list.save()


        response['msg'] = newListName
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def add_word(request):

    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8')).get('words')


    try:
        for k in data:
            print(k['word'])
            hasWord = Word.objects.filter(word=k['word'])
            if hasWord.count() == 0:
                to_add = Word(word=k['word'],
                              phonetic_symbol=k['phonetic_symbol'],
                              definition_cn = k['definition_cn'],
                              definition_en = k['definition_en'],
                              pronunciation_path = k['pronunciation_path']
                              )
                to_add.save()

        response['msg'] = data
        response['state']=True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)