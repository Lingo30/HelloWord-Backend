from django.db import models

class UserInfo(models.Model):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(null=True)
    password_hash = models.CharField(max_length=64, unique=True)
    daily_words_count = models.IntegerField(null=True,default=200)

class Word(models.Model):
    word = models.CharField(max_length=32)
    phonetic_symbol = models.CharField(max_length=32)
    definition_cn = models.CharField(max_length=64)
    definition_en = models.CharField(max_length=255, null=True)
    pronunciation_path = models.CharField(max_length=64, null=True)

class WordList(models.Model):
    list_name = models.CharField(max_length=64)
    list_author_name = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=255, null=True)
    word_count = models.IntegerField(null=True)
    gen_type = models.IntegerField(null=True)

class WordListItem(models.Model):
    word_list_id = models.ForeignKey("WordList", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)

class UserStudyWordInfo(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)
    mastery_level = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField()
    forget_times = models.IntegerField(default=0)
    simple = models.BooleanField(default=False)

class UserStudyList(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    list_name = models.CharField(max_length=64)
    word_count = models.IntegerField(null=True)
    last_study_date = models.DateField()

class UserStudyListItem(models.Model):
    user_study_list_id = models.ForeignKey("UserStudyList", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)

class WordRelation(models.Model):
    word_id = models.ForeignKey("Word", related_name='first_word', on_delete=models.CASCADE)
    related_word_id = models.ForeignKey("Word", related_name='related_word', on_delete=models.CASCADE)
    relation_type = models.CharField(max_length=10)

class Example(models.Model):
    example_sentence = models.CharField(max_length=255)

class WordExample(models.Model):
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)
    example_id = models.ForeignKey("Example", on_delete=models.CASCADE)

class Photo(models.Model):
    photo_path = models.CharField(max_length=64)

class WordPhoto(models.Model):
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)
    photo_id = models.ForeignKey("Photo", on_delete=models.CASCADE)

class WordsStory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    story = models.CharField(max_length=1023)
    answers = models.CharField(max_length=255)

class WordsCloze(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    cloze = models.CharField(max_length=1023)
    answers = models.CharField(max_length=255)

class ReadingHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    input = models.CharField(max_length=1023)
    output = models.CharField(max_length=1023)

class WritingHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    input = models.CharField(max_length=1023)
    output = models.CharField(max_length=1023)

class ChatHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    communication = models.CharField(max_length=1023)