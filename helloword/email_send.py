from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

import random
import datetime


from django.http import JsonResponse

import json
from helloword.models import UserInfo,EmailToken

from pathlib import Path
import sys
import os

with open('env.json') as env:
    ENV = json.load(env)

def gen_vcode(length=4):
    # 返回一个随机字符串，生成4位验证码
    return ''.join(random.choices('0123456789abcdefghigklmnopqrstuvwxyz', k=length))

# 格式化编码，以防乱码
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 构建发送邮件对象
def gen_vcode_msg(vcode, from_addr, to_addr):
    """
        vcode: 发送的验证码
        from_addr: 发送方邮箱
        to_addr: 接收方邮箱
        return: 返回含有发送验证码的MIMEText对象
    """
    text = f'您好，欢迎注册HelloWord。您的验证码是：{vcode},有效期为20分钟, 请立即验证。'
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = _format_addr('HelloWord<%s>' % from_addr)
    msg['To'] = _format_addr('新用户<%s>' % to_addr)
    msg['Subject'] = Header('HelloWord注册验证码', 'utf-8').encode()
    return msg


def send_vcode(smtp_server, from_addr, password, to_addr):
    """
        smtp_server: 当前使用smtp(qq邮箱)服务器
        from_addr: 发送方邮箱
        password: 发送方邮箱密码（授权码）
        to_addr: 接收方邮箱

    """
    # 构建一个 smtp 对象
    server = smtplib.SMTP(smtp_server, 25)
    # 设置一个调试级别（上线可以关闭）
    server.set_debuglevel(1)
    # 登录
    server.login(from_addr, password)
    # 构造要发送邮件的内容
    vcode = gen_vcode()  # 验证码
    msg = gen_vcode_msg(vcode, from_addr, to_addr)  # 邮件对象
    # 发送邮件
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()  # 退出
    return vcode


def send(addr):
    from_addr = 'mmmusel@163.com'
    to_addr = addr
    password = 'UONHQRCNUSPVXSNJ'
    smtp_server = 'smtp.163.com'
    code = send_vcode(smtp_server, from_addr, password, to_addr)
    print('发送的验证码：', code)
    return code

def send_email_code(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        email_addr = data.get('email_addr')
        try:
            code = send(email_addr)
        except Exception as e:
            response['msg'] = '邮件格式错误 请重试'
            return JsonResponse(response)
        t=EmailToken.objects.filter(email_addr=email_addr)
        if t.count()!=0:
            email_token=t[0]
            email_token.token=code
            email_token.save()
        else:
            email_token = EmailToken(email_addr=email_addr,
                                     token=code)
            email_token.save()

        response['state']=True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

def check_email_code(request):
    response = {}
    response['state'] = False

    try:
        data = json.loads(request.body.decode())
        email_addr = data.get('email_addr')

        code = data.get('code')

        t=EmailToken.objects.filter(email_addr=email_addr,token=code)
        if t.count()!=0:

            email_token=t[0]
            if datetime.datetime.now()-email_token.gen_time>datetime.timedelta(minutes=20):
                response['msg']='注册码已失效，请重试'
                return JsonResponse(response)
            response['state']=True
        else:
            response['msg'] = '邮箱验证码错误'
            return JsonResponse(response)

        response['state']=True
    except Exception as e:
        response['msg'] = str(e)

    return JsonResponse(response)

