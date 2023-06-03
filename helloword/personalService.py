
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import json
import datetime
from helloword.models import Word,UserInfo,FileInfo,UserStudyWordInfo
from helloword.models import WordList,WordListItem,UserStudyList,UserStudyListItem
from helloword.userInfo import checkCookie, wrapRes
from chatgpt import client
from chatgpt.tools import wordlist, utils
import pdfplumber
import re
from zhon.hanzi import punctuation

# TODO:增加id及次数控制、加锁

dailly_times = 5
def get_wordlist_from_tags(request):
    response = {}
    response['state'] = False
    data = json.loads(request.body.decode())
    user_id = data.get('userId')

    try:
        tags = data.get('tags')

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)

        times_left = dailly_times - FileInfo.objects.filter(user_id_id=user_obj,
                                                            post_time__gte=datetime.date.today()).count()

        if user_obj.vip_time and user_obj.vip_time > datetime.datetime.now():
            times_left += 2

        if times_left == 0:
            response['last_times'] = 0
            response['msg'] = '今天的词单创建次数已经用完啦！明天再来吧'
            user_obj.gpt_lock = ""
            user_obj.save()
            return JsonResponse(response)

        message = wordlist.gen_wordlist_from_keywords(tags)
        rcv_message = client.Client().send_message(message)
        print(rcv_message)
        extract_words = str(re.findall(r"[\[](.*?)[\]]", rcv_message)[0]).split(', ')

        lower_extract_words=[]
        for i in extract_words:
            lower_extract_words.append(i.lower())

        response['words']=list(set(lower_extract_words))

        ret = []
        word_list = Word.objects.filter(word__in=lower_extract_words)
        if word_list.count()==0:
            response['msg']='所给关键词未生成有效单词，换一个主题词吧~'
            return JsonResponse(response)

        for k in word_list:
            cur = {
                'wordId':k.id,
                'word':k.word,
                'meaning':k.definition_cn.replace("\\n","\n").replace("\\r","")
            }
            ret.append(cur)

        response['wordlist']=ret
        response['state'] = True

        file = open("../file_tmp.txt",'w')

        newfile = FileInfo(file_info=file, user_id=user_obj)
        newfile.save()

        times_left -= 1
        response['msg'] = '词单生成成功~今日剩余次数：' + str(times_left)
        response['last_times'] = times_left

        user_obj.gpt_lock = ""
        user_obj.save()
        return wrapRes(response, user_id)


    except Exception as e:
        response['msg'] = str(e)
    try:

        user_obj = UserInfo.objects.get(id=user_id)
        user_obj.gpt_lock = ""
        user_obj.save()
    except Exception as e:
        response['msg'] = str(e)
    return JsonResponse(response)


def get_wordList_smart_from_file(request):

    response = {}
    response['state'] = False

    user_id_tmp = -1

    try:
        str_tmp = str(request.FILES.get('userId').read())[2:-1].replace("\"", "")
        print(str_tmp)
        user_id = int(str_tmp)
        user_id_tmp=user_id

        if not checkCookie(request,response,user_id):
            return JsonResponse(response)
        user_obj = UserInfo.objects.get(id=user_id)


        file = request.FILES.get('file')
        newfile = FileInfo(file_info=file,user_id=user_obj)

        times_left = dailly_times - FileInfo.objects.filter(user_id_id=user_obj,
                                                               post_time__gte=datetime.date.today()).count()

        if user_obj.vip_time and user_obj.vip_time > datetime.datetime.now():
            times_left += 2

        if times_left == 0:
            response['last_times'] = 0
            response['msg'] = '今天的词单创建次数已经用完啦！明天再来吧'
            user_obj.gpt_lock = ""
            user_obj.save()
            return JsonResponse(response)

        newfile.save()

        filepath = 'media/'+str(newfile.file_info)
        print(filepath)

        content = ''
        with pdfplumber.open(filepath) as pdf:
            page_num = 1
            words = []
            for page in pdf.pages:
                if page_num > 3:
                    break
                else:
                    page_num += 1
                mv_chinese = re.sub('[\u4e00-\u9fa5]', '', page.extract_text())
                words.append(re.sub("[{}]+".format(punctuation), " ", mv_chinese))

            content=' '.join(words)
            print(content)

        message = wordlist.gen_wordlist_from_passage(content)
        rcv_message = client.Client().send_message(message)
        print(rcv_message)
        extract_words = str(re.findall(r"[\[](.*?)[\]]", rcv_message)[0]).split(', ')

        lower_extract_words=[]
        for i in extract_words:
            lower_extract_words.append(i.lower())

        response['words']=list(set(lower_extract_words))

        ret = []
        word_list = Word.objects.filter(word__in=lower_extract_words)
        if word_list.count()==0:
            response['msg']='输入文件不包含有效单词'
            return JsonResponse(response)

        for k in word_list:
            cur = {
                'wordId':k.id,
                'word':k.word,
                'meaning':k.definition_cn.replace("\\n","\n").replace("\\r","")
            }
            ret.append(cur)

        response['wordlist']=ret
        response['state'] = True


        times_left -= 1
        response['msg'] = '词单提取成功~今日剩余次数：' + str(times_left)
        response['last_times'] = times_left

        user_obj.gpt_lock = ""
        user_obj.save()
        return wrapRes(response, user_id)


    except Exception as e:
        response['msg'] = str(e)
    try:
        if user_id_tmp!=-1:
            user_obj = UserInfo.objects.get(id=user_id_tmp)
            user_obj.gpt_lock = ""
            user_obj.save()
    except Exception as e:
        response['msg'] = str(e)
    return JsonResponse(response)
