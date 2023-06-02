from django.test import TestCase
from rest_framework.test import APITransactionTestCase, RequestsClient
from helloword.models import UserInfo, WordList, Word, WordListItem, UserStudyList, UserStudyListItem, EmailToken, \
    EmailResetToken, WritingHistory, WordsStory, WordsCloze
from datetime import datetime
import requests
import json

# Create your tests here.

verify = 'FX2N'
imgCode = 'U88A'

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
    userInfo.cookie_token = 'abcd'
    userInfo.save()

def email_init(email_addr):
    code = '1234'
    email_token = EmailToken(email_addr=email_addr,
                             token=code)
    email_token.save()

class UserRegisterTest(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0',
            id= 1
        )
        to_add.save()

    def test_register(self):
        '''测试注册用户'''
        email_addr = '111@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode, 'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['data']['wordNum'], 200)

    def test_noname(self):
        '''测试用户名不能为空'''
        email_addr = '333@qq.com'
        email_init(email_addr)
        test_data = {'name': '', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名不能为空')

    def test_namerepeat(self):
        '''测试用户名重复'''
        email_addr = '444@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user3', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        email_addr = '555@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user3', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名重复')

    def test_wrong_code(self):
        '''测试验证码错误'''
        email_addr = '222@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user2', 'password': '123456', 'verify': 'verify', 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '验证码错误')

    def test_wrong_email_code(self):
        '''测试邮箱验证码错误'''
        email_addr = '666@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user6', 'password': '123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '12'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '邮箱验证码错误')

    def test_email_repeat(self):
        '''测试邮箱重复'''
        email_addr = '777@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user7', 'password': '123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        response = self.client.post('/register/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '该邮箱已注册')


class UserLoginTest(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0',
            id = 1
        )
        to_add.save()
        email_addr = '111@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': 'FX2N', 'imgCode': 'U88A',
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")

    def test_login(self):
        '''测试登录用户'''
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        self.assertEqual(resp['state'], True)

    def test_wrong_password(self):
        '''测试密码错误'''
        test_data = {'name': 'user1', 'password': '123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '密码错误')

    def test_wrong_name(self):
        '''测试用户名不存在'''
        test_data = {'name': 'user', 'password': '123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名不存在')

    def test_wrong_code(self):
        '''测试验证码错误'''
        test_data = {'name': 'user1', 'password': '123456', 'verify': 'verify', 'imgCode': imgCode}
        response = self.client.post('/login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '验证码错误')


class UserCookieLogin(TestCase):
    def setUp(self) -> None:
        test_init()

    def test_cookie_login(self):
        '''测试利用cookie登录'''
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'userId': user.id}
        response = self.client.post('/cookie_login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_miss_cookie(self):
        '''测试不存在cookie'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'userId': user.id}
        response = self.client.post('/cookie_login/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], 'token失效，请重新登录')


class UserGetVerifyImg(TestCase):
    def setUp(self) -> None:
        pass

    def test_get_verify_img(self):
        '''测试获取图形验证码'''
        response = self.client.post('/get_verify_img/', {}, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)


class UserAdminLoginTest(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0',
            id = 1
        )
        to_add.save()
        email_addr = '111@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': 'FX2N', 'imgCode': 'U88A',
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")

    def test_admin_login(self):
        '''测试登录用户'''
        userInfo = UserInfo.objects.get(username='user1')
        userInfo.user_type = 'admin'
        userInfo.save()
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/adminLogin/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        self.assertEqual(resp['state'], True)

    def test_normal_login(self):
        '''测试登录普通用户'''
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/adminLogin/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '没有管理员权限')

    def test_wrong_password(self):
        '''测试密码错误'''
        test_data = {'name': 'user1', 'password': '123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/adminLogin/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '密码错误')

    def test_wrong_name(self):
        '''测试用户名不存在'''
        test_data = {'name': 'user', 'password': '123456', 'verify': verify, 'imgCode': imgCode}
        response = self.client.post('/adminLogin/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名不存在')

    def test_wrong_code(self):
        '''测试验证码错误'''
        test_data = {'name': 'user1', 'password': '123456', 'verify': 'verify', 'imgCode': imgCode}
        response = self.client.post('/adminLogin/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '验证码错误')

class UserChangePWD(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

    def test_change_pwd(self):
        '''修改密码'''
        user = UserInfo.objects.get(username='user1')
        print(user.id)
        test_data = {'user_id': user.id, 'old_pwd': 'user123456', 'new_pwd': '123456user'}
        response = self.client.post('/change_pwd/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

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
            list_name='初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0',
            id=1
        )
        to_add.save()
        email_addr = '111@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': 'FX2N', 'imgCode': 'U88A',
                     'email': email_addr, 'code': '1234'}
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
        tags = ['aaa', 'bbb', 'ccc']
        userinfo = {'name': 'user10', 'tags': tags}
        test_data = {'user_id': user.id, 'user_info': userinfo}
        response = self.client.post('/submit_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)


class UserResetPassword(TestCase):
    def setUp(self) -> None:
        to_add = WordList(
            list_name= '初始词单',
            list_author_name='HelloWord团队',
            description='平台新用户初始化词单',
            gen_type='0',
            id=1
        )
        to_add.save()
        email_addr = '111@qq.com'
        email_init(email_addr)
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': 'FX2N', 'imgCode': 'U88A',
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/register/', test_data, content_type="application/json")
        email_addr = '111@qq.com'
        code = '1234'
        email_token = EmailResetToken(email=email_addr,
                                      token=code)
        email_token.save()

    def test_reset_password(self):
        '''测试重置密码'''
        email_addr = '111@qq.com'
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode, 'email': email_addr, 'code': '1234'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_noname(self):
        '''测试用户名不能为空'''
        email_addr = '111@qq.com'
        test_data = {'name': '', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], False)
        #self.assertEqual(resp['msg'], '用户名不能为空')

    def test_no_user(self):
        '''测试用户名不存在'''
        email_addr = '111@qq.com'
        test_data = {'name': 'user', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode, 'email': email_addr, 'code': '1234'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户名不存在')


    def test_wrong_email(self):
        '''测试'''
        email_addr = '222@qq.com'
        test_data = {'name': 'user1', 'password': 'user123456', 'verify': verify, 'imgCode': imgCode, 'email': email_addr, 'code': '1234'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '输入邮箱与用户名不匹配')

    def test_wrong_code(self):
        '''测试验证码错误'''
        email_addr = '111@qq.com'
        test_data = {'name': 'user1', 'password': '123456', 'verify': 'verify', 'imgCode': imgCode,
                     'email': email_addr, 'code': '1234'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '验证码错误')

    def test_wrong_email_code(self):
        '''测试邮箱验证码错误'''
        email_addr = '111@qq.com'
        test_data = {'name': 'user1', 'password': '123456', 'verify': verify, 'imgCode': imgCode,
                     'email': email_addr, 'code': '12'}
        response = self.client.post('/reset_password/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '邮箱验证码错误')


class Wordlist(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

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

    def test_get_today_learned_words_sum(self):
        '''测试获取今日单词学习数量'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'userId': user.id}
        response = self.client.post('/get_today_learned_words_sum/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_set_daily_num(self):
        '''测试更改今日单词学习数量'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'userId': user.id, 'num': 20}
        response = self.client.post('/set_daily_num/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)


class LearnWord(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

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
        #self.assertEqual(resp['state'], True)
        #self.assertEqual(resp['list_id'], user.last_study_list.id)

    def test_get_search_word(self):
        '''测试搜索单词'''
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'word': 'aaa'}
        response = self.client.post('/get_search_word/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)
        self.assertEqual(resp['word'], 'aaa')

    def test_get_search_word(self):
        '''测试搜素失败'''
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'word': '111'}
        response = self.client.post('/get_search_word/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '查询单词不存在')

    '''def test_reset_study_list(self):
        user = UserInfo.objects.get(username='user1')
        study_list = UserStudyList.objects.get(user_id=user)
        word = Word.objects.get(word='aaa')
        test_data = {'study_list_id': study_list.id}
        response = self.client.post('/reset_study_list/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)'''

class Chat(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

    def test_user_send(self):
        '''测试chat功能'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'user_id': user.id, 'question': 'hello!'}
        #response = self.client.post('/user_send/', test_data, content_type="application/json")
        #resp = response.json()
        #print(resp)
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
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

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
        self.assertEqual(resp['state'], True)
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

class FeedBack(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

    def test_feedback(self):
        '''测试用户反馈'''
        user = UserInfo.objects.get(username='user1')
        modules = ['111', '222', '333']
        test_data = {'userId': user.id, 'type': 'a', 'modules': modules, 'content': '123456'}
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_feedback_more_than_4(self):
        '''测试用户反馈'''
        user = UserInfo.objects.get(username='user1')
        modules = ['111', '222', '333']
        test_data = {'userId': user.id, 'type': 'a', 'modules': modules, 'content': '123456'}
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        response = self.client.post('/add_feedback/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '今天的反馈已经收到啦~明天再来吧')


class ReviewHistory(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

    def test_get_record_info0(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WritingHistory(
            user_id= user,
            input= 'aaa',
            output= 'bbb'
        )
        history.save()
        test_data = {'user_id': user.id, 'type': 0, 'record_id': history.id}
        response = self.client.post('/get_record_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_record_info1(self):
        '''测试获取单词复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsStory(
            user_id= user,
            story= 'aaa',
            answers= 'bbb'
        )
        history.save()
        test_data = {'user_id': user.id, 'type': 1, 'record_id': history.id}
        response = self.client.post('/get_record_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_record_info2(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsCloze(
            user_id= user,
            cloze='models.CharField(max_length=4096, null=True)',
            answers = 'models.CharField(max_length=255, null=True)',
            words = 'models.CharField(max_length=255, null=True)',
            eordlist = 'models.CharField(max_length=255, null=True)'
        )
        history.save()
        test_data = {'user_id': user.id, 'type': 2, 'record_id': history.id}
        response = self.client.post('/get_record_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_get_record_info3(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsCloze(
            user_id= user,
            cloze='models.CharField(max_length=4096, null=True)',
            answers = 'models.CharField(max_length=255, null=True)',
            words = 'models.CharField(max_length=255, null=True)',
            eordlist = 'models.CharField(max_length=255, null=True)'
        )
        history.save()
        test_data = {'user_id': user.id, 'type': 3, 'record_id': history.id}
        response = self.client.post('/get_record_info/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '类型不存在')

    def test_get_history_record_id0(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WritingHistory(
            user_id= user,
            input= 'aaa',
            output= 'bbb'
        )
        history.save()
        now = datetime.now()
        d = {
            'year': now.year,
            'month': now.month,
            'day': now.day
        }
        test_data = {'user_id': user.id, 'type': 0, 'record_id': history.id, 'start_date': d, 'end_date': d}
        response = self.client.post('/get_history_record_id/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_history_record_id1(self):
        '''测试获取单词复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsStory(
            user_id= user,
            story= 'aaa',
            answers= 'bbb'
        )
        history.save()
        now = datetime.now()
        d = {
            'year': now.year,
            'month': now.month,
            'day': now.day
        }
        test_data = {'user_id': user.id, 'type': 1, 'record_id': history.id, 'start_date': d, 'end_date': d}
        response = self.client.post('/get_history_record_id/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_history_record_id2(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsCloze(
            user_id= user,
            cloze='models.CharField(max_length=4096, null=True)',
            answers = 'models.CharField(max_length=255, null=True)',
            words = 'models.CharField(max_length=255, null=True)',
            eordlist = 'models.CharField(max_length=255, null=True)'
        )
        history.save()
        now = datetime.now()
        d = {
            'year': now.year,
            'month': now.month,
            'day': now.day
        }
        test_data = {'user_id': user.id, 'type': 2, 'record_id': history.id, 'start_date': d, 'end_date': d}
        response = self.client.post('/get_history_record_id/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_get_history_record_id3(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WritingHistory(
            user_id= user,
            input= 'aaa',
            output= 'bbb'
        )
        history.save()
        now = datetime.now()
        d = {
            'year': now.year,
            'month': now.month,
            'day': now.day
        }
        test_data = {'user_id': user.id, 'type': 3, 'record_id': history.id, 'start_date': d, 'end_date': d}
        response = self.client.post('/get_history_record_id/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '类型不存在')

    def test_get_story_record(self):
        '''测试获取单词复习故事历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsStory(
            user_id= user,
            story= 'aaa',
            answers= 'bbb'
        )
        history.save()
        test_data = {'user_id': user.id, 'record_id': history.id}
        response = self.client.post('/get_story_record/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_writing_record(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WritingHistory(
            user_id= user,
            input= 'aaa',
            output= 'bbb'
        )
        history.save()
        test_data = {'user_id': user.id, 'record_id': history.id}
        response = self.client.post('/get_writing_record/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)

    def test_get_blank_record(self):
        '''测试获取写作复习历史'''
        user = UserInfo.objects.get(username='user1')
        history = WordsCloze(
            user_id= user,
            cloze='models.CharField(max_length=4096, null=True)',
            answers = 'models.CharField(max_length=255, null=True)',
            words = 'models.CharField(max_length=255, null=True)',
            eordlist = 'models.CharField(max_length=255, null=True)'
        )
        history.save()
        test_data = {'user_id': user.id, 'record_id': history.id}
        response = self.client.post('/get_blank_record/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        #self.assertEqual(resp['state'], True)


class Message(TestCase):
    def setUp(self) -> None:
        test_init()
        cookie = self.client.cookies
        cookie['user_token'] = 'abcd'

    def test_send_to_all(self):
        '''测试集体通知'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'adminId': user.id, 'message': 'message'}
        response = self.client.post('/send_to_all/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_send_message_to_user(self):
        '''测试单独通知'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'adminId': user.id, 'message': 'message', 'userId': user.id}
        response = self.client.post('/send_message_to_user/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], True)

    def test_send_message_to_user_wrong(self):
        '''测试用户不存在'''
        user = UserInfo.objects.get(username='user1')
        test_data = {'adminId': user.id, 'message': 'message', 'userId': 0}
        response = self.client.post('/send_message_to_user/', test_data, content_type="application/json")
        resp = response.json()
        print(resp)
        self.assertEqual(resp['state'], False)
        self.assertEqual(resp['msg'], '用户id不存在')