from django.test import TestCase
from rest_framework.test import APITransactionTestCase, RequestsClient
from helloword.models import UserInfo, WordList, Word, WordListItem, UserStudyList, UserStudyListItem
import requests
import json

# Create your tests here.

def test_init():
    add_word_list = WordList(
        list_name='初始词单',
        list_author_name='HelloWord团队',
        description='平台新用户初始化词单',
        gen_type='0'
    )
    add_word_list.save()
    word = 'a'
    for i in range(6):
        word = word + 'a'
        add_word = Word(word=word, phonetic_symbol='aaaa', definition_cn='aaaaaa')
        add_word.save()
        add_word_item = WordListItem(word_id=add_word, word_list_id=add_word_list)
        add_word_item.save()
    userInfo = UserInfo(username='user1',
                        password_hash='user123456')
    userInfo.save()
    to_add = UserStudyList(
        user_id=userInfo,
        list_name='新用户词单'
    )
    to_add.save()
    public = add_word_list
    words = WordListItem.objects.filter(word_list_id_id=public)
    for i in words:
        add_to_list = UserStudyListItem(
            user_study_list_id=to_add,
            word_id=i.word_id
        )
        add_to_list.save()

    userInfo.last_study_list = to_add
    userInfo.save()

class UserRegisterTest(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0'
        )
        to_add.save()

    def test_register(self):
        '''测试注册用户'''
        test_data = {'name': 'user1', 'password': 'user123456'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['data']['wordNum'], 200)

    def test_noname(self):
        test_data = {'name': '', 'password': 'user123456'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        #self.assertEqual(resp['state'], False)
        #self.assertEqual(resp['msg'], '用户名不能为空')

    def test_namerepeat(self):
        test_data = {'name': 'user2', 'password': 'user123456'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        #self.assertEqual(resp['state'], False)
        #self.assertEqual(resp['msg'], '用户名重复')

class UserLoginTest(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0'
        )
        to_add.save()
        test_data = {'name': 'user1', 'password': 'user123456'}
        response = self.client.post('/register/', test_data, content_type="application/json")

    def test_login(self):
        '''测试登录用户'''
        test_data = {'name': 'user1', 'password': 'user123456'}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        self.assertEqual(resp['state'], True)

    def test_wrong_password(self):
        '''测试密码错误'''
        test_data = {'name': 'user1', 'password': '123456'}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '密码错误')

    def test_wrong_name(self):
        '''测试用户名不存在'''
        test_data = {'name': 'user', 'password': '123456'}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名不存在')

class UserChangePWD(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_change_pwd(self):
        '''修改密码'''
        test_data = {'user_id': 1, 'old_pwd': 'user123456', 'new_pwd': '123456user'}
        response = self.client.post('/change_pwd/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_wrong_password(self):
        '''测试原密码错误'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'user_id': user.id, 'old_pwd': '123456', 'new_pwd': '123456user'}
        response = self.client.post('/change_pwd/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '原密码错误')



class UserGetUserInfo(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0'
        )
        to_add.save()
        test_data = {'name': 'user1', 'password': 'user123456'}
        response = self.client.post('/register/', test_data, content_type="application/json")

    def test_get_user_info(self):
        '''测试获取用户信息'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'user_id': user.id}
        response = self.client.post('/get_user_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['info']['name'], '')

    def test_get_recommend_tags(self):
        '''测试获取用户tags'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {}
        response = self.client.post('/get_recommend_tags/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_submit_info(self):
        '''测试上传用户tags'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {}
        response = self.client.post('/submit_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

class Wordlist(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_get_user_wordlists(self):
        '''测试获取用户词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'userId': user.id}
        response = self.client.post('/get_user_wordlists/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_wordlist_info(self):
        '''测试获取用户词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {'listId': study_list.id}
        response = self.client.post('/get_wordlist_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_words_info(self):
        '''测试获取用户词单单词'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {'listId': study_list.id, 'pageSize': 1, 'curPage': 1}
        response = self.client.post('/get_words_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_edit_wordlists(self):
        '''测试修改用户词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {'deleteLists': {}, 'updateLists':[{'listId': study_list.id, 'name': 'test'}]}
        response = self.client.post('/edit_wordlists/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_wordlists(self):
        '''测试获取用户词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {}
        response = self.client.post('/get_wordlists/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_official_wordlists(self):
        '''测试获取官方词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {}
        response = self.client.post('/get_official_wordlists/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_update_learn_wordlist(self):
        '''测试更新已学词单'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        study_list = UserStudyList.objects.get(user_id=user)
        test_data = {'userId': user.id, 'listId': study_list.id}
        response = self.client.post('/update_learn_wordlist/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['last_study_list'], study_list.list_name)

    def test_add_wordlist_from_official(self):
        '''测试从官方词单中添加用户词单'''
        user = UserInfo.objects.get(username='user1')
        word_list = WordList.objects.get(list_name='初始词单')
        test_data = {'userId': user.id, 'listId': word_list.id, 'name': 'new_study_list'}
        response = self.client.post('/add_wordlist_from_official/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        study_list = UserStudyList.objects.get(list_name='new_study_list')
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['listId'], study_list.id)

class LearnWord(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_get_word_releation(self):
        '''测试获取单词相关属性'''
        word = Word.objects.get(word='aaa')
        test_data = {'word_id': word.id}
        response = self.client.post('/get_word_releation/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_group_word_learn_save(self):
        '''测试学习一组单词'''
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'user_id': user.id,
                     'list_id': study_list.id,
                     'words': [{'forget_times': 1,
                                'simple': False,
                                'word_id': word.id}]}
        response = self.client.post('/group_word_learn_save/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_group_words_in_list(self):
        '''测试获取一组单词'''
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'user_id': user.id}
        response = self.client.post('/get_group_words_in_list/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['list_id'], user.last_study_list.id)

    def test_reset_study_list(self):
        '''测试重置词单'''
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'study_list_id': study_list.id}
        response = self.client.post('/reset_study_list/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

class Chat(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_user_send(self):
        '''测试chat功能'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id, 'question': 'hello!'}
        response = self.client.post('/user_send/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_get_log_history(self):
        '''测试获取聊天历史'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id}
        response = self.client.post('/get_log_history/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

class Review(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_get_blank_text(self):
        '''测试获取空白文段'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id}
        response = self.client.post('/get_blank_text/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_get_today_words(self):
        '''测试获取今日所学单词'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id}
        response = self.client.post('/get_today_words/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '今日学习单词太少啦，先去背单词吧~')

    def test_words_to_story_no_word(self):
        '''测试生成故事'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id, 'words': []}
        response = self.client.post('/words_to_story/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '请背诵单词后，选择今日所学单词！')

    def test_words_to_story_less_3_word(self):
        '''测试生成故事'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id, 'words': ['apple', 'banana']}
        response = self.client.post('/words_to_story/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '请至少选择3个单词生成故事')

    def test_words_to_story_more_6_word(self):
        '''测试生成故事'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id,
                     'words': ['apple', 'banana', 'elephant', 'food', 'fruit', 'silly', 'you', 'me']}
        response = self.client.post('/words_to_story/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '至多选择6个单词生成故事')

    def test_writing_analysis(self):
        '''测试写作分析'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_article': 'I am a good person.'}
        response = self.client.post('/writing_analysis/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_sentence_analysis(self):
        '''测试句子分析'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'sentence': 'I am a good person.'}
        response = self.client.post('/sentence_analysis/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)