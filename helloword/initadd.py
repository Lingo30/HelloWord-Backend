from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json

from helloword.models import Word,UserInfo,Example,WordExample,WordRelation,FileInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem

def add_relation(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8'))
    word_a = data.get('word_a')
    word_b = data.get('word_b')

    if (word_a == word_b):
        response['msg'] = '单词重复'
        return JsonResponse(response)

    if (word_b<word_a):
        t=word_b
        word_b=word_a
        word_a=t
    type = data.get('type')

    try:
        word_a_obj = Word.objects.get(word=word_a)
        word_b_obj = Word.objects.get(word=word_b)

        if (WordRelation.objects.filter(word_id=word_a_obj,related_word_id=word_b_obj)):
            response['msg'] = '已存在关系'
            return JsonResponse(response)

        new_WordRelation = WordRelation(
            word_id=word_a_obj,
            related_word_id=word_b_obj,
            relation_type=type
        )
        new_WordRelation.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

# 一个例句link一个已有单词
def add_example(request):

    response = {}
    response['state'] = False
    data = json.loads(request.body.decode('utf-8'))
    word = data.get('word')
    example_str = data.get('example')

    try:
        word_obj = Word.objects.get(word=word)
        if Example.objects.filter(example_sentence=example_str).count()==0:
            new_example = Example(
                example_sentence=example_str
            )
            new_example.save()

        example_obj=Example.objects.get(example_sentence=example_str)

        if (WordExample.objects.filter(word_id=word_obj,example_id=example_obj)):
            response['msg'] = '例句已存在'
            return JsonResponse(response)

        new_WordExample = WordExample(
            word_id=word_obj,
            example_id = example_obj
        )
        new_WordExample.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

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
                user_study_list_id=to_add,
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


def file_to_public(request):
    response = {}
    response['state'] = False

    newListName = '新用户词单'

    try:
        file = request.FILES.get('file')
        newfile = FileInfo(file_info=file)
        newfile.save()

        filepath = 'media/' + str(newfile.file_info)
        contents = open(filepath, 'r').read()
        print(contents)
        words = []

        oneword = ''

        for c in contents:
            if c.isalpha():
                oneword += c
            else:
                if len(oneword) > 0:
                    words.append(oneword.lower())
                oneword = ''

        print(words)
        response['words'] = words

        ret = []
        word_list = Word.objects.filter(word__in=words)
        if word_list.count() == 0:
            response['msg'] = '输入文件不包含有效单词'
            return JsonResponse(response)

        to_add = WordList(
            list_name=newListName,
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0'
        )
        to_add.save()

        for k in word_list:
            add_to_list = WordListItem(
                word_list_id=WordList.objects.get(id=to_add.id),
                word_id=k
            )
            add_to_list.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)