from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
import random
import re

from helloword.models import Word,UserInfo,Example,WordExample,WordRelation,UserStudyWordInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem,DailyNum
from helloword.userInfo import checkCookie, wrapRes


def get_user_statistic(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        user_id = data.get('user_id')
        if not checkCookie(request, response, user_id):
            return JsonResponse(response)

        user_obj = UserInfo.objects.get(id=user_id)
        response['today_target'] = user_obj.daily_words_count

        response['today_num'] = 0
        today_study = DailyNum.objects.filter(user_id_id=user_obj,post_time=datetime.datetime.today())
        if today_study.count()!=0:
            response['today_num']=today_study[0].num

        study_word_history = DailyNum.objects.filter(user_id_id=user_obj)
        ret_date=[]
        ret_num=[]
        for i in study_word_history:
            time = i.post_time.timetuple()
            rm0time = str(time.tm_year) + "-" + str(time.tm_mon) + "-" + str(time.tm_mday)
            ret_date.append(rm0time)
            ret_num.append(i.num)

        response['history_date']=ret_date
        response['history_num']=ret_num

        delta = datetime.datetime.today().weekday()
        mon = datetime.datetime.today()-datetime.timedelta(days=delta)
        weeknum=0
        ret_week=[]
        for i in range(0,7):
            today_study = DailyNum.objects.filter(user_id_id=user_obj, post_time=mon+datetime.timedelta(days=i))
            if today_study.count() != 0:
                ret_week.append(today_study[0].num)
                weeknum+=today_study[0].num
            else:
                ret_week.append(0)
        response['week_num']=weeknum
        response['week_data']=ret_week

        response['state']=True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_info_by_id(word_id,response):
    try:
        base_word = Word.objects.get(id=word_id)

        example_sen = '暂无例句'
        example_objs = WordExample.objects.filter(word_id_id=base_word)
        example_count = example_objs.count()
        if example_count > 0:
            # TODO
            p = random.randint(0, example_count - 1)
            example_sen = example_objs[p].example_id.example_sentence + '\n' + example_objs[
                p].example_id.example_translation

        synonyms_list = []
        antonyms_list = []

        word_relation_objs = WordRelation.objects.filter(word_id_id=base_word)
        for k in word_relation_objs:
            if k.relation_type == 'synonym' and len(synonyms_list) < 3:
                cur = {
                    'word_id': k.related_word_id.id,
                    'word': k.related_word_id.word,
                    'definition_cn': k.related_word_id.definition_cn.replace("\\n", "\n").replace("\\r", ""),
                    'phonetic_symbol': k.related_word_id.phonetic_symbol
                }
                synonyms_list.append(cur)
            elif k.relation_type == 'antonym' and len(antonyms_list) < 3:
                cur = {
                    'word_id': k.related_word_id.id,
                    'word': k.related_word_id.word,
                    'definition_cn': k.related_word_id.definition_cn.replace("\\n", "\n").replace("\\r", ""),
                    'phonetic_symbol': k.related_word_id.phonetic_symbol
                }
                antonyms_list.append(cur)

        word_relation_objs = WordRelation.objects.filter(related_word_id_id=base_word)
        for k in word_relation_objs:
            if k.relation_type == 'synonym' and len(synonyms_list) < 3:
                cur = {
                    'word_id': k.word_id.id,
                    'word': k.word_id.word,
                    'definition_cn': k.word_id.definition_cn.replace("\\n", "\n").replace("\\r", ""),
                    'phonetic_symbol': k.related_word_id.phonetic_symbol
                }
                synonyms_list.append(cur)
            elif k.relation_type == 'antonym' and len(antonyms_list) < 3:
                cur = {
                    'word_id': k.word_id.id,
                    'word': k.word_id.word,
                    'definition_cn': k.word_id.definition_cn.replace("\\n", "\n").replace("\\r", ""),
                    'phonetic_symbol': k.related_word_id.phonetic_symbol
                }
                antonyms_list.append(cur)

        response['synonyms'] = synonyms_list
        response['antonyms'] = antonyms_list
        response['example'] = example_sen
        response['state'] = True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def get_search_word(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    try:
        word_string = data.get('word')
        response['word'] = word_string
        search_word_list = Word.objects.filter(word=word_string)
        if search_word_list.count() == 0:
            response['msg'] = '查询单词不存在'
            return JsonResponse(response)
        fetchword = search_word_list[0]
        response['phonetic_symbol'] = fetchword.phonetic_symbol
        response['definition_cn'] = fetchword.definition_cn.replace("\\n", "\n").replace("\\r", "")
        get_info_by_id(fetchword.id, response)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def reset_study_list(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    study_list_id = data.get('study_list_id')

    try:
        reset = UserStudyList.objects.get(id=study_list_id)
        reset.head = 0
        reset.save()
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_word_releation(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    word_id = data.get('word_id')

    try:
        get_info_by_id(word_id,response)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def group_word_learn_save(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')
    ret_words = data.get('words')
    list_id = data.get('list_id')

    new_head = 0

    print(ret_words)


    try:
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)

        user_study = UserStudyList.objects.get(id = list_id)
        user = UserInfo.objects.get(id=user_id)
        for k in ret_words:
            word = Word.objects.get(id=k['word_id'])
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
                t = UserStudyListItem.objects.filter(word_id_id=word,user_study_list_id=user_study)[0]
                if t.id > new_head:
                    new_head = t.id
            else :
                f=studyinfo[0].forget_times
                m=studyinfo[0].mastery_level
                s=studyinfo[0]
                s.forget_times=f+k['forget_times']
                s.simple = k['simple']
                s.mastery_level=m+1
                s.save()

        study_list = user.last_study_list
        study_list.head = new_head
        study_list.save()

        study_count = UserStudyWordInfo.objects.filter(user_id_id=user,last_reviewed__gte=datetime.date.today()).count()
        today_study = DailyNum.objects.filter(user_id_id=user, post_time=datetime.datetime.today())
        if today_study.count() != 0:
            today_obj = today_study[0]
            today_obj.num = study_count
            today_obj.save()
            response['word_num'] = study_count
        else:
            today_obj = DailyNum(user_id=user,num=study_count)
            today_obj.save()
            response['word_num'] = study_count

        user_obj = user
        if study_count == 100:
            if (not user_obj.vip_time) or user_obj.vip_time < (datetime.datetime.today()+datetime.timedelta(days=1)):
                user_obj.vip_time = datetime.datetime.today()+datetime.timedelta(days=1)
                user_obj.save()

        response['new_head'] = new_head
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


def get_group_words_in_list(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')


    try:
        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user = UserInfo.objects.get(id=user_id)

        # 用户是否有单词书
        if not user.last_study_list:
            response['hasBook'] = False
            return JsonResponse(response)

        response['hasBook'] = True


        # user_list_id = 1
        #UserStudyListItem_head = 0
        #new_head=0
        userlist_obj = user.last_study_list
        UserStudyListItem_head = userlist_obj.head
        new_head = UserStudyListItem_head


        new = []

        newlist = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__gt=UserStudyListItem_head).order_by('id')
        # 去掉别的词单学过的
        for k in newlist:
            if len(new)>3:
                break

            # TODO 重置此单功能删除本行逻辑
            if UserStudyWordInfo.objects.filter(user_id_id=user,word_id_id=k.word_id).count()==0:
                new.append(k.word_id.id)
                print('kkk'+str(k.word_id.id))
            new_head=k.id

        # 新单词全部背完; TODO 需要增加重置逻辑
        if len(new) == 0:
            if not userlist_obj.has_done:
                userlist_obj.has_done=True
                userlist_obj.save()
            return JsonResponse(response)

        review = []
        size = 10-len(new)
        # 去掉今天复习过的
        review_list = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__lte=UserStudyListItem_head).values('word_id')
        #print(review_list)
        info_list = UserStudyWordInfo.objects.filter(user_id_id=user,word_id__in=review_list)
        #print(info_list)
        acttmp = info_list.exclude(last_reviewed__gte=datetime.date.today()).exclude(simple=True)
        for p in acttmp:
            print('mmmmmm'+str(p.id))
        act = []
        for m in acttmp:
            act.append(m.word_id.id)
            print('ttt' + str(k.word_id.id))

        if(len(act)<size):
            newlist = UserStudyListItem.objects.filter(user_study_list_id=userlist_obj).filter(id__gt=new_head).order_by('id')
            # 去掉别的词单学过的
            for k in newlist:
                if len(new)+len(act) > 9:
                    break

                if UserStudyWordInfo.objects.filter(user_id_id=user, word_id_id=k.word_id).count() == 0:
                    new.append(k.word_id.id)
                    print('ggg' + str(k.word_id.id))
                new_head = k.id

        # TODO 补充复习单词逻辑 现在从之前学习过的词中random

        if len(act)>size:
            s=random.sample(act, size)
            for y in s:
                print('ppp'+str(y))
            new.extend(s)
        else:
            for y in act:
                print('jjj'+str(y))
            new.extend(act)

        print(new)
        random.shuffle(new)


        ret=[]
        for pp in new:
            fetchword = Word.objects.get(id=pp)

            full = {
                'id': fetchword.id,
                'word': fetchword.word,
                'phonetic_symbol': fetchword.phonetic_symbol,
                'definition_cn': fetchword.definition_cn.replace("\\n","\n").replace("\\r",""),
                'definition_en': fetchword.definition_en.replace("\\n","\n").replace("\\r",""),
                'word_id': fetchword.id,
            }

            base_word = Word.objects.get(id=pp)

            example_sen = '暂无例句'
            example_objs = WordExample.objects.filter(word_id_id=base_word)
            if example_objs.count() > 0:
                # TODO 补充例句返回逻辑 现在返回首个例句
                example_sen = example_objs[0].example_id.example_sentence + example_objs[0].example_id.example_translation

            synonyms_list = []
            antonyms_list = []

            word_relation_objs = WordRelation.objects.filter(word_id_id=base_word)
            for k in word_relation_objs:
                if k.relation_type == 'synonym' and len(synonyms_list) < 3:
                    cur = {
                        'word_id': k.related_word_id.id,
                        'word': k.related_word_id.word,
                        'definition_cn': k.related_word_id.definition_cn.replace("\\n","\n").replace("\\r","")
                    }
                    synonyms_list.append(cur)
                elif k.relation_type == 'antonym' and len(antonyms_list) < 3:
                    cur = {
                        'word_id': k.related_word_id.id,
                        'word': k.related_word_id.word,
                        'definition_cn': k.related_word_id.definition_cn.replace("\\n","\n").replace("\\r","")
                    }
                    antonyms_list.append(cur)

            word_relation_objs = WordRelation.objects.filter(related_word_id_id=base_word)
            for k in word_relation_objs:
                if k.relation_type == 'synonym' and len(synonyms_list) < 3:
                    cur = {
                        'word_id': k.word_id.id,
                        'word': k.word_id.word,
                        'definition_cn': k.word_id.definition_cn.replace("\\n","\n").replace("\\r","")
                    }
                    synonyms_list.append(cur)
                elif k.relation_type == 'antonym' and len(antonyms_list) < 3:
                    cur = {
                        'word_id': k.word_id.id,
                        'word': k.word_id.word,
                        'definition_cn': k.word_id.definition_cn.replace("\\n","\n").replace("\\r","")
                    }
                    antonyms_list.append(cur)

            full['synonyms'] = synonyms_list
            full['antonyms'] = antonyms_list
            full['example'] = example_sen


            ret.append(full)

        response['group_words']=ret
        response['list_id']=userlist_obj.id
        response['state'] = True
        return wrapRes(response, user_id)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)