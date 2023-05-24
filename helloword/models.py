from django.db import models

class UserInfo(models.Model):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(null=True)
    password_hash = models.CharField(max_length=64)
    daily_words_count = models.IntegerField(null=True,default=200)
    user_avatar = models.ImageField(upload_to="user_avatar/", null=True, default="user_avatar/default_avatar.jpg")
    last_study_list = models.ForeignKey("UserStudyList", null = True, on_delete=models.SET_NULL)

    last_study_date = models.CharField(max_length=128, null = True, default="")
    study_days_count = models.IntegerField(null=True,default=0)
    not_unique_name = models.CharField(max_length=64,null=True)

    tags = models.CharField(max_length=2048,null=True,default='音乐 电影')

    last_study_date_info=models.DateTimeField(auto_now=True,null=True)

    cookie_token = models.CharField(max_length=128,null=True)

    gpt_lock=models.CharField(max_length=128,null=True,default="")
    user_type = models.CharField(max_length=128, null=True, default="")

    invite_code = models.CharField(max_length=64, null=True)
    has_invite = models.IntegerField(default=0)
    vip_time = models.DateTimeField(null=True)

class EmailToken(models.Model):
    email_addr = models.CharField(max_length=64, unique=True)
    token = models.CharField(max_length=32)
    gen_time = models.DateTimeField(auto_now=True)
    has_register = models.BooleanField(default=False,null=True)

class EmailResetToken(models.Model):
    email = models.CharField(max_length=64, unique=True)
    token = models.CharField(max_length=32)
    gen_time = models.DateTimeField(auto_now=True)

class FileInfo(models.Model):
    file_info = models.FileField(upload_to="user_file/")
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE,null=True)

class Word(models.Model):
    word = models.CharField(max_length=64, unique=True)
    phonetic_symbol = models.CharField(max_length=64)
    definition_cn = models.CharField(max_length=2048)
    definition_en = models.CharField(max_length=2048, null=True)
    pronunciation_path = models.CharField(max_length=128, null=True)
    pos = models.CharField(max_length=32, null=True)
    tag = models.CharField(max_length=32, null=True)
    collins = models.IntegerField(null=True, default=0)
    oxford = models.IntegerField(null=True, default=0)
    bnc = models.IntegerField(null=True, default=0)
    frq = models.IntegerField(null=True, default=0)
    exchange = models.CharField(max_length=128, null=True)

class WordList(models.Model):
    list_name = models.CharField(max_length=64)
    list_author_name = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=255, null=True)
    word_count = models.IntegerField(null=True)
    gen_type = models.IntegerField(null=True)

    list_author = models.ForeignKey("UserInfo", null = True, on_delete=models.SET_NULL)
    create_type = models.CharField(max_length=128, null=True, default="")
    # create_type和description

class WordListItem(models.Model):
    word_list_id = models.ForeignKey("WordList", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)

class UserStudyWordInfo(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)
    mastery_level = models.IntegerField(default=0)
    last_reviewed = models.DateField(auto_now=True, null=True)
    forget_times = models.IntegerField(default=0)
    simple = models.BooleanField(default=False)

class UserStudyList(models.Model):
    user_id = models.ForeignKey("UserInfo", related_name='study',on_delete=models.CASCADE)
    list_name = models.CharField(max_length=64)
    word_count = models.IntegerField(null=True)
    last_study_date = models.DateField(auto_now=True)
    head = models.IntegerField(null=True, default=0)

    list_author = models.ForeignKey("UserInfo", related_name='create',null=True, on_delete=models.SET_NULL)
    has_done = models.BooleanField(null=True, default=False)
    create_type = models.CharField(max_length=128, null=True, default="")
    # create_type 由于保证alpha已有数据的一致性，当create_type='private'的时候表示用户新建立的私人词单。或者以往数据list_author=null为私人词单
    # 官方词单create_type='official'，或者为null
    # alpha阶段数据中，私人词单的list_auther为user_id，公共拉取的词单的list_auther为null或”“

class UserStudyListItem(models.Model):
    user_study_list_id = models.ForeignKey("UserStudyList", on_delete=models.CASCADE)
    word_id = models.ForeignKey("Word", on_delete=models.CASCADE)



class WordRelation(models.Model):
    word_id = models.ForeignKey("Word", related_name='first_word', on_delete=models.CASCADE)
    related_word_id = models.ForeignKey("Word", related_name='related_word', on_delete=models.CASCADE)
    relation_type = models.CharField(max_length=10)

class Example(models.Model):
    example_sentence = models.CharField(max_length=2048, default="")
    example_translation = models.CharField(max_length=2048, default="")

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
    story = models.CharField(max_length=4096, null=True)
    answers = models.CharField(max_length=255, null=True)

    post_time = models.DateTimeField(auto_now=True, null=True)

class WordsCloze(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    cloze = models.CharField(max_length=4096, null=True)
    answers = models.CharField(max_length=255, null=True)

    words = models.CharField(max_length=255,null=True)
    eordlist = models.CharField(max_length=255,null=True)

    post_time = models.DateTimeField(auto_now=True, null=True)



class ReadingHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    input = models.CharField(max_length=4096, null=True)
    output = models.CharField(max_length=4096, null=True)

    post_time = models.DateTimeField(auto_now=True, null=True)

class WritingHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    input = models.CharField(max_length=4096, null=True)
    output = models.CharField(max_length=4096, null=True)

    post_time = models.DateTimeField(auto_now=True, null=True)

class ChatHistory(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    message = models.CharField(max_length=8192, null=True)
    type = models.BooleanField(null=True)
    post_time = models.DateTimeField(auto_now=True, null=True)

class Feedback(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    type = models.CharField(max_length=64,default="")
    modules = models.CharField(max_length=512,default="")
    content = models.CharField(max_length=1024)
    post_time = models.DateTimeField(auto_now_add=True, null=True)
    has_read = models.BooleanField(default=False)


class BroadcastMessage(models.Model):
    message = models.CharField(max_length=1024)
    post_time = models.DateTimeField(auto_now_add=True)

class UserMessage(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    message = models.CharField(max_length=1024)
    post_time = models.DateTimeField(auto_now_add=True)
    has_read = models.BooleanField(default=False)

class PublicListCheck(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    # 作者
    user_study_list_id = models.ForeignKey("UserStudyList", null=True, on_delete=models.SET_NULL)
    # 对于已经提交审核过的词单，删除掉未被审核与拒绝审核的审核信息
    # 对于接受审核的词单，将user_study_list_id字段设置为null。如果展示词单详细信息，可以使用public_list_id
    post_time = models.DateTimeField(auto_now_add=True)
    # 用户提交审核时间
    check_time = models.DateTimeField(auto_now=True)
    # 管理员审核时间
    check_status = models.CharField(max_length=128, null=True, default="user_submit")
    # user_submit  accept  reject
    public_list_id = models.ForeignKey("WordList", on_delete=models.CASCADE,null=True)
    # 审核accept后，拉取的官方词单的id；默认官方词单不会被删除
    send_message = models.ForeignKey("UserMessage", null=True, on_delete=models.SET_NULL)
    # 审核意见

class DailyNum(models.Model):
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    post_time = models.DateField(auto_now_add=True)
    num = models.IntegerField(default=0)


