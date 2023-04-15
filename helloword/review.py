from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
import json
from helloword.models import UserStudyWordInfo
from helloword.models import Word
from helloword.models import WordsStory

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
            # TODO gpt生成story
            story = 'gpt story'
            answer = ' '.join(words)
            words_story = WordsStory(user_id=user_id, story=story, answers=answer)
            words_story.save()
            response['story'] = story


    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

# blank text
'''def get_blank_text(request):
    response = {}
    response['state'] = False

    data = json.loads(request.body.decode())

    user_id = data.get('user_id')

    try:
        now_date = timezone.now().date()
        today_words = UserStudyWordInfo.objects.filter(user_id_id=user_id, last_reviewed=now_date)
        words = []
        if len(today_words)

    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

# writing
# def writing_analysis(request):'''
