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
from chatgpt.tools import vocabulary, reading, writing

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
            this_word = Word.objects.get(id=item.word_id)
            cur = {
                'id': this_word.id,
                'word': this_word.word
            }
            words.append(cur)
        response['today_words'] = words
        response['state'] = True
        response['msg'] = 'success'
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def words_to_story(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')
    words = data.get('words')

    try:
        if not words:
            response['msg'] = '请选择单词！'
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
def get_blank_text(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')

    try:
        now_date = timezone.now().date()
        today_words = UserStudyWordInfo.objects.filter(user_id_id=user_id, last_reviewed=now_date).order_by('-forget_times')
        words = []
        # TODO 测试阶段没有单词学习数据，所以随机给5个词，与学习部分对接后改为抛异常提示今日未学习单词
        if len(today_words) < 5:
            words = ['assign', 'involve', 'skeleton', 'uncover', 'entertainment']
            response['state'] = True
            # response['msg'] = 'please begin today's study'
        else:
            for i in range(5):
                word = Word.objects.get(id=today_words[i].word_id).word
                words.append(word)
            response['state'] = True
        message = vocabulary.gen_cloze_from_words(words)
        cloze = client.Clinet().send_message(message)
        # first convert cloze from string to JSON and then extract article and answer from cloze in JSON format
        cloze = json.loads(cloze)
        article = cloze['content']
        # wordlist = cloze['answer']
        wordlist = []
        for word in words:
            target = '$' + word + '$'
            start = article.index(target)
            end = start + len(target)
            cur = {
                'start': start,
                'end': end
            }
            wordlist.append(cur)
        response['content'] = article
        response['wordList'] = wordlist


    except Exception as e:
        response['state'] = False
        response['msg'] = str(e)

    return JsonResponse(response)

# writing
def writing_analysis(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    # user_id = data.get('user_id') beta阶段再考虑存历史记录
    user_article = data.get('user_article')

    try:
        message = writing.analyze_essay(user_article)
        output = client.Clinet().send_message(message)
        output = json.loads(output)
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['comment'] = output
        response['state'] = True
        print(output)
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def sentence_analysis(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    # user_id = data.get('user_id') beta阶段再考虑存历史记录
    user_sentence = data.get('sentence')

    try:
        # TODO 用翻译api或gpt分析sentence，句子信息在sentence，分析结果输出到output
        message = reading.analyze_sentence_alone(user_sentence)
        output = client.Clinet().send_message(message)
        output = json.loads(output)
        translation = output['content']
        structure = output['structure']
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['translation'] = translation
        response['structure'] = structure
        response['state'] = True
        response['msg'] = 'success'
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)