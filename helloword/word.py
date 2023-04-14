from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
import random

from helloword.models import Word,UserInfo,Example,WordExample,WordRelation,UserStudyWordInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem

def get_word_releation(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    word_id = data.get('word_id')

    try:
        base_word = Word.objects.get(id=word_id)

        example_sen='暂无例句'
        example_objs = WordExample.objects.filter(word_id_id=base_word)
        if example_objs.count()>0:
            # TODO
            example_sen=example_objs[0].example_id.example_sentence

        synonyms_list=[]
        antonyms_list=[]

        word_relation_objs = WordRelation.objects.filter(word_id_id=base_word)
        for k in word_relation_objs:
            if k.relation_type == 'synonyms' and len(synonyms_list) < 3:
                cur = {
                    'word_id': k.related_word_id.id,
                    'word': k.related_word_id.word,
                    'definition_cn': k.related_word_id.definition_cn
                }
                synonyms_list.append(cur)
            elif k.relation_type == 'antonyms' and len(antonyms_list) < 3:
                cur = {
                    'word_id': k.related_word_id.id,
                    'word': k.related_word_id.word,
                    'definition_cn': k.related_word_id.definition_cn
                }
                antonyms_list.append(cur)

        word_relation_objs = WordRelation.objects.filter(related_word_id_id=base_word)
        for k in word_relation_objs:
            if k.relation_type == 'synonyms' and len(synonyms_list) < 3:
                cur = {
                    'word_id': k.word_id.id,
                    'word': k.word_id.word,
                    'definition_cn': k.word_id.definition_cn
                }
                synonyms_list.append(cur)
            elif k.relation_type == 'antonyms' and len(antonyms_list) < 3:
                cur = {
                    'word_id': k.word_id.id,
                    'word': k.word_id.word,
                    'definition_cn': k.word_id.definition_cn
                }
                antonyms_list.append(cur)

        response['synonyms'] = synonyms_list
        response['antonyms'] = antonyms_list
        response['example'] = example_sen
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def group_word_learn_save(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')
    ret_words = data.get('words')


    try:
        user = UserInfo.objects.get(id=user_id)
        for k in ret_words:
            word = Word.objects.get(id=k['id'])
            studyinfo = UserStudyWordInfo.objects.filter(user_id_id=user,word_id_id=word)
            if studyinfo.count()==0:
                new_studyinfo = UserStudyWordInfo(
                    user_id=user,
                    word_id=word,
                    forget_times = k['forget_times'],
                    mastery_level=1,
                    simple=k['simple']
                )
                new_studyinfo.save()
            else :
                f=studyinfo[0].forget_times
                m=studyinfo[0].mastery_level
                s=studyinfo[0]
                s.forget_times=f+k['forget_times']
                s.simple = k['simple']
                s.mastery_level=m+1
                s.save()


        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_group_words_in_list(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')


    try:
        user = UserInfo.objects.get(id=user_id)

        # TODO
        user_list_id = 2
        UserStudyListItem_head = 7
        new_head=7
        userlist_obj = UserStudyList.objects.get(id=user_list_id)


        new = []

        newlist = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__gt=UserStudyListItem_head).order_by('id')
        # 去掉别的词单学过的
        for k in newlist:
            if len(new)>3:
                break

            if UserStudyWordInfo.objects.filter(user_id_id=user,word_id_id=k.word_id).count()==0:
                new.append(k.word_id.id)
            new_head=k.id

        #print(new)

        review = []
        size = 10-len(new)
        # 去掉今天复习过的
        review_list = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__lte=UserStudyListItem_head).values('word_id')
        #print(review_list)
        info_list = UserStudyWordInfo.objects.filter(word_id__in=review_list)
        #print(info_list)
        act = list(info_list.exclude(last_reviewed__date__gte=datetime.date.today()+datetime.timedelta(days=1)).values_list('id', flat=True))
        #print(act)

        if(len(act)<size):
            newlist = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__gt=new_head).order_by('id')
            # 去掉别的词单学过的
            for k in newlist:
                if len(new)+len(act) > 9:
                    break

                if UserStudyWordInfo.objects.filter(user_id_id=user, word_id_id=k.word_id).count() == 0:
                    new.append(k.word_id.id)
                new_head = k.id

        if len(act)>size:
            new.extend(random.sample(act, size))
        else:
            new.extend(act)

        random.shuffle(new)
        print(new)

        ret=[]
        for pp in new:
            fetchword = Word.objects.get(id=pp)

            full = {
                'id': fetchword.id,
                'word': fetchword.word,
                'phonetic_symbol': fetchword.phonetic_symbol,
                'definition_cn': fetchword.definition_cn,
                'definition_en': fetchword.definition_en,
                'word_id': fetchword.id,
            }

            base_word = Word.objects.get(id=pp)

            example_sen = '暂无例句'
            example_objs = WordExample.objects.filter(word_id_id=base_word)
            if example_objs.count() > 0:
                # TODO
                example_sen = example_objs[0].example_id.example_sentence

            synonyms_list = []
            antonyms_list = []

            word_relation_objs = WordRelation.objects.filter(word_id_id=base_word)
            for k in word_relation_objs:
                if k.relation_type == 'synonyms' and len(synonyms_list) < 3:
                    cur = {
                        'word_id': k.related_word_id.id,
                        'word': k.related_word_id.word,
                        'definition_cn': k.related_word_id.definition_cn
                    }
                    synonyms_list.append(cur)
                elif k.relation_type == 'antonyms' and len(antonyms_list) < 3:
                    cur = {
                        'word_id': k.related_word_id.id,
                        'word': k.related_word_id.word,
                        'definition_cn': k.related_word_id.definition_cn
                    }
                    antonyms_list.append(cur)

            word_relation_objs = WordRelation.objects.filter(related_word_id_id=base_word)
            for k in word_relation_objs:
                if k.relation_type == 'synonyms' and len(synonyms_list) < 3:
                    cur = {
                        'word_id': k.word_id.id,
                        'word': k.word_id.word,
                        'definition_cn': k.word_id.definition_cn
                    }
                    synonyms_list.append(cur)
                elif k.relation_type == 'antonyms' and len(antonyms_list) < 3:
                    cur = {
                        'word_id': k.word_id.id,
                        'word': k.word_id.word,
                        'definition_cn': k.word_id.definition_cn
                    }
                    antonyms_list.append(cur)

            full['synonyms'] = synonyms_list
            full['antonyms'] = antonyms_list
            full['example'] = example_sen


            ret.append(full)

        response['group_words']=ret
        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)