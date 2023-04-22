from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
import json
from helloword.models import UserStudyWordInfo
from helloword.models import Word
from helloword.models import WordsStory
from helloword.models import WritingHistory

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
                'id': item.word_id,
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
            # TODO gpt生成story，输入在words中，输出到story
            story = 'gpt story'
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
                word = Word.objects.get(id=today_words[i].word_id)
                words.append(word)
            response['state'] = True
        # TODO 调用gpt获取完整文章，输入为words，输出到article
        article = ' is '.join(words) # 先给个静态数据用于测试
        wordlist = []
        for word in words:
            start = article.index(word)
            end = start + len(word)
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
        # TODO gpt 分析writing，文章信息在user_article，分析结果输出到output
        output = 'gpt writing output'
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['comment'] = output
        response['state'] = True
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
        output = 'gpt sentence output'
        # writing_history = WritingHistory(user_id=user_id, input=user_article, output=output)
        # writing_history.save()
        response['translation'] = output
        response['state'] = True
        response['msg'] = 'success'
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)