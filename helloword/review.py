import random

from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
import json
import datetime
from helloword.models import UserStudyWordInfo
from helloword.models import Word,UserInfo
from helloword.models import WordsStory,WordsCloze,WritingHistory,ReadingHistory
from helloword.models import WritingHistory
from chatgpt import client
from chatgpt.tools import vocabulary, reading, writing, utils
import re
dailly_times = 3

# story
def get_today_words(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    now_date = timezone.now().date()

    try:
        today_words = UserStudyWordInfo.objects.filter(user_id_id=user_id, last_reviewed=now_date)
        words = []
        for item in today_words:
            this_word = item.word_id
            cur = {
                'id': this_word.id,
                'word': this_word.word
            }
            words.append(cur)
        if len(words) < 5:
            response['msg'] = '今日学习单词太少啦，先去背单词吧~'
            response['today_words']=words
            response['state'] = True
            return JsonResponse(response)
        response['today_words'] = words
        response['state'] = True
        response['msg'] = 'success'
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


# WordsStory
def words_to_story(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    words = data.get('words')

    try:
        if not words:
            response['msg'] = '请背诵单词后，选择今日所学单词！'
            return JsonResponse(response)
        elif len(words) < 3:
            response['msg'] = '请至少选择3个单词生成故事'
            return JsonResponse(response)
        elif len(words) > 6:
            response['msg'] = '至多选择6个单词生成故事'
            return JsonResponse(response)
        else:
            user_obj = UserInfo.objects.get(id=user_id)
            words_story = WordsStory(user_id=user_obj)
            times_left = dailly_times-WordsStory.objects.filter(user_id_id = user_obj,post_time__gte=datetime.date.today()).count()
            if times_left==0:
                response['msg'] = '今天的故事模式次数已经用完啦！明天再来吧'
                response['last_times'] = 0
                return JsonResponse(response)
            words_story.save()

            message = vocabulary.gen_story_from_words(words)
            story = client.Clinet().send_message(message)
            answer = ' '.join(words)
            

            words_story.story=story
            words_story.answers = answer

            words_story.save()
            response['story'] = story

            times_left-=1
            response['msg'] = '今日剩余次数：'+str(times_left)
            response['last_times']=times_left

            response['state'] = True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


# blank text
# WordsCloze
def get_blank_text(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')

    try:

        #
        user_obj = UserInfo.objects.get(id=user_id)
        times_left = dailly_times - WordsCloze.objects.filter(user_id_id=user_obj,
                                                              post_time__gte=datetime.date.today()).count()


        if times_left == 0:
            response['msg'] = '今天的完形填空次数已经用完啦！明天再来吧'
            response['last_times'] = 0
            return JsonResponse(response)

        now_date = timezone.now().date()
        today_words = UserStudyWordInfo.objects.filter(user_id_id=user_id, last_reviewed=now_date)
        words = []


        #TODO
        today_count=len(today_words)
        if today_count < 5:
            response['msg'] = '今日学习单词太少啦，先去背几个新单词吧~'
            response['content'] = ''
            response['wordList'] = []
            response['answer'] = []
            response['originWords'] = []
            return JsonResponse(response)

            # words = ['assign', 'involve', 'skeleton', 'uncover', 'entertainment']
            # response['state'] = True
            # response['msg'] = 'please begin today's study'
        else:
            random_index = random.sample(range(today_count), 5)
            for i in random_index:
                word = today_words[i].word_id.word
                words.append(word)

        print(word)

        message = vocabulary.gen_cloze_from_words(words)
        outputk = client.Clinet().send_message(message)

        output = utils.extract_json(outputk)
        # 如果解析结果为None，则重新执行一次
        if output == None:
            outputk = client.Clinet().send_message(message)
            output = utils.extract_json(outputk)
        # 如果结果还为None，则返回错误信息
        if output == None:
            response['msg'] = '解析失败，请重新输入'
            return JsonResponse(response)

        cloze = json.loads(output)
        article = cloze['content']
        answer = cloze['answer']
        wordlist = []

        print(article)
        print(answer)


        str_index = []
        tar_obj=re.finditer(r"\$.*?\$",article)
        for target in tar_obj:
            #target = '$' + word + '$'
            start = target.start()
            end = target.end()

            cur = {
                'start': start,
                'end': end
            }
            wordlist.append(cur)
            str_index.append(start)
            str_index.append(end)
        response['content'] = article
        response['wordList'] = wordlist
        response['answer'] = answer
        response['originWords'] = words

        times_left -= 1
        response['msg'] = '今日剩余次数：' + str(times_left)
        response['last_times'] = times_left

        s1 = article
        s2 = ' '.join(answer)
        s3 = ' '.join(words)
        s4 = ' '.join(str(i) for i in str_index)

        w = WordsCloze(user_id=user_obj,cloze=s1,answers=s2,words=s3,eordlist=s4)
        w.save()

        response['state'] = True


    except Exception as e:
        response['state'] = False
        response['msg'] = str(e)

    return JsonResponse(response)


# WritingHistory
def writing_analysis(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    # user_id = data.get('user_id') beta阶段再考虑存历史记录
    user_article = data.get('user_article')
    user_id = data.get('user_id')

    try:
        user_obj = UserInfo.objects.get(id=user_id)
        times_left = dailly_times - WritingHistory.objects.filter(user_id_id=user_obj,
                                                              post_time__gte=datetime.date.today()).count()
        if times_left == 0:
            response['msg'] = '今天的作文分析次数已经用完啦！明天再来吧'
            response['last_times'] = 0
            return JsonResponse(response)

        message = writing.analyze_essay(user_article)
        outputk = client.Clinet().send_message(message)
        output = utils.extract_json(outputk)

        print(output)
        print(outputk)

        if output == None:
            response['msg'] = '不是合法文章，请注意写作规范哦'
            return JsonResponse(response)


        print(output)
        print(outputk)
        output = json.loads(outputk)
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['comment'] = output

        print(output)

        s1 = user_article
        s2 = outputk

        times_left -= 1
        response['msg'] = '今日剩余次数：' + str(times_left)
        response['last_times'] = times_left



        w = WritingHistory(user_id=user_obj, input=s1, output=s2)
        w.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)


# ReadingHistory
def sentence_analysis(request):
    response = {}
    response['state'] = False


    data = json.loads(request.body.decode())
    user_id = data.get('user_id')

    # user_id = data.get('user_id') beta阶段再考虑存历史记录
    user_sentence = data.get('sentence')



    try:
        user_obj = UserInfo.objects.get(id=user_id)
        times_left = dailly_times - ReadingHistory.objects.filter(user_id_id=user_obj,
                                                              post_time__gte=datetime.date.today()).count()
        if times_left == 0:
            response['msg'] = '今天的长难句分析次数已经用完啦！明天再来吧'
            response['last_times'] = 0
            return JsonResponse(response)

        # TODO 用翻译api或gpt分析sentence，句子信息在sentence，分析结果输出到output
        message = reading.analyze_sentence_alone(user_sentence)
        outputk = client.Clinet().send_message(message)
        output = utils.extract_json(outputk)
        # 如果解析结果为None，则重新执行一次
        if output == None:
            outputk = client.Clinet().send_message(message)
            output = utils.extract_json(outputk)
        # 如果结果还为None，则返回错误信息
        if output == None:
            response['msg'] = '解析失败，请重新输入'
            return JsonResponse(response)

        output = json.loads(output)
        translation = output['content']
        structure = output['structure']
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['translation'] = translation
        response['structure'] = structure

        response['msg'] = 'success'

        s1 = user_sentence
        s2 = outputk

        times_left -= 1
        response['msg'] = '今日剩余次数：' + str(times_left)
        response['last_times'] = times_left

        w = ReadingHistory(user_id=user_obj, input=s1, output=s2)
        w.save()

        response['state'] = True

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)