from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
import json
from helloword.models import UserStudyWordInfo
from helloword.models import Word
from helloword.models import WordsStory
from helloword.models import WritingHistory
from chatgpt import client
from chatgpt.tools import vocabulary, reading, writing, utils

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
        elif len(words)<3:
            response['msg'] = '请至少选择3个单词生成故事'
            return JsonResponse(response)
        elif len(words)>6:
            response['msg'] = '至多选择6个单词生成故事'
            return JsonResponse(response)
        else:
            message = vocabulary.gen_story_from_words(words)
            story = client.Clinet().send_message(message)
            answer = ' '.join(words)
            words_story = WordsStory(user_id_id=user_id, story=story, answers=answer)
            words_story.save()
            response['story'] = story
            response['state'] = True
            response['msg'] = 'success'
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
        now_date = timezone.now().date()
        today_words = UserStudyWordInfo.objects.filter(user_id_id=user_id, last_reviewed=now_date).order_by('-forget_times')
        words = []

        if len(today_words) < 5:
            response['msg'] = '今日学习单词太少啦，先去背单词吧~'
            response['content'] = ''
            response['wordList'] = []
            response['answer'] = []
            response['originWords'] = []
            return JsonResponse(response)

            #words = ['assign', 'involve', 'skeleton', 'uncover', 'entertainment']
            #response['state'] = True
            # response['msg'] = 'please begin today's study'
        else:
            for i in range(5):
                word = today_words[i].word_id.word
                words.append(word)
            response['state'] = True
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

        str_index=[]
        for word in answer:
            target = '$' + word + '$'
            start = article.index(target)
            end = start + len(target)
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

        s1 = article
        s2 = ' '.join(answer)
        s3 = ' '.join(words)
        s4 = ' '.join(str(i) for i in str_index)


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

    try:
        message = writing.analyze_essay(user_article)
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
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['comment'] = output
        response['state'] = True
        print(output)

        s1 = user_article
        s2 = outputk

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

# ReadingHistory
def sentence_analysis(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    # user_id = data.get('user_id') beta阶段再考虑存历史记录
    user_sentence = data.get('sentence')

    try:
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
        response['state'] = True
        response['msg'] = 'success'

        s1 = user_sentence
        s2 = outputk

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)