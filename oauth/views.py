#coding:utf-8
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse #url逆向解析

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.forms.models import model_to_dict #模型对象转字典

from .oauth_client import OAuth_Base
from .models import OAuth_ex, OAuth_type
from .forms import BindEmail

import time
import uuid

def _get_oauth(type_name, state):
    """获取对应的OAuth对象"""
    try:
        oauth_type = OAuth_type.objects.get(type_name = type_name)
    except:
        raise Http404

    kw = model_to_dict(oauth_type)
    kw['state'] = state
    return OAuth_Base.Get_OAth(**kw)

def _login_error_response(message, jump_url):
    """登录出错跳转页面"""
    data = {}
    data['message'] = u'登录出错，请稍后重试<br>(辅助信息：%s)”' % (message or u"无")
    data['goto_url'] = jump_url
    data['goto_time'] = 3000
    data['goto_page'] = True
    return render_to_response('message.html', data)

def _bind_email_response(open_id, nickname, type_name, jump_url):
    """绑定邮箱页面"""
    url = '%s?open_id=%s&nickname=%s&oauth_type=%s&state=%s' % (reverse('bind_email'), open_id, nickname, type_name, jump_url)
    return HttpResponseRedirect(url)

def _bind_success_response(jump_url):
    """绑定并登录成功跳转页面"""
    data = {}
    data['goto_url'] = jump_url
    data['goto_time'] = 3000
    data['goto_page'] = True
    data['message'] = u'登录并绑定成功'
    return render_to_response('message.html', data)

def _get_account_from_email(oauth_id, email, open_id, nickname):
    """通过邮箱获取用户"""
    #判断是否存在对应的用户(我这里的用户名就是邮箱，根据你的实际情况参考)
    users = User.objects.filter(username = email)

    if users:
        #存在则绑定和登录
        user = users[0]
    else:
        #不存在则直接注册并登录
        user = User(username = email, email = email)
        pwd = str(uuid.uuid1()) #生成随机密码
        user.set_password(pwd)
        user.is_active = True #真实邮箱来源，则认为是有效用户
        user.save()

    #添加绑定记录
    oauth_type = OAuth_type.objects.get(id = oauth_id)
    oauth_ex = OAuth_ex(user = user, openid = open_id, oauth_type = oauth_type)
    oauth_ex.save()

    #更新昵称
    if not user.first_name:
        user.first_name = nickname
        user.save()
    return user

def _login_user(request, user):
    """直接登录用户"""
    #设置backend，绕开authenticate验证
    setattr(user, 'backend', 'django.contrib.auth.backends.ModelBackend')
    login(request, user)


def oauth_login(request, type_name):
    #获取oauth对象
    state = request.GET.get('state') #获取登录页面记录的上一个网页网址信息
    oauth = _get_oauth(type_name, state)

    #获取 得到Authorization Code的地址
    url = oauth.get_auth_url()
    return HttpResponseRedirect(url)

def qq_check(request):
    """登录之后，会跳转到这里。需要判断code和state"""
    request_code = request.GET.get('code')
    state = request.GET.get('state') or '/'
    oauth = _get_oauth('QQ', state)

    try:
        #获取access_token
        access_token = oauth.get_access_token(request_code)

        #稍微休息一下，避免发送urlopen的10060错误
        time.sleep(0.05)    
        open_id = oauth.get_open_id()   
    except Exception as e:
        #登录出错跳转到错误提示页面
        return _login_error_response(e.message, state)

    #检查open_id是否存在
    qqs = OAuth_ex.objects.filter(openid = open_id, oauth_type = oauth.id)
    if qqs:
        #存在则获取对应的用户，并登录
        _login_user(request, qqs[0].user)
        return HttpResponseRedirect(state) #跳转前验证这个网址？
    else:
        #不存在，则跳转到绑定邮箱页面
        infos = oauth.get_user_info()    #获取用户信息
        nickname = infos['nickname']
        return _bind_email_response(open_id, nickname, oauth.oauth_type, state)

def sina_check(request):
    """登录之后，会跳转到这里。需要判断code和state"""
    request_code = request.GET.get('code')
    state = request.GET.get('state') or '/'
    oauth = _get_oauth('Sina', state)

    #获取access_token
    try:
        access_token = oauth.get_access_token(request_code)
        time.sleep(0.05)    #稍微休息一下，避免发送urlopen的10060错误
        open_id = oauth.get_open_id()
    except Exception as e:
        #登录出错跳转到错误提示页面
        return _login_error_response(e.message, state)

    #检查uid是否存在
    sinas = OAuth_ex.objects.filter(openid = open_id, oauth_type = oauth.id)
    if sinas:
        #存在则获取对应的用户，并登录
        _login_user(request, sinas[0].user)
        return HttpResponseRedirect(state)
    else:
        #不存在，则尝试获取邮箱
        try:
            #获取得到邮箱则直接绑定
            email = oauth.get_email()
        except Exception as e:
            #获取不到则跳转到邮箱绑定页面
            #获取用户资料
            infos = oauth.get_user_info()
            nickname = infos['screen_name']
            return _bind_email_response(open_id, nickname, oauth.oauth_type, state)

        #获取到邮箱，直接绑定
        #判断是否存在对应的用户(我这里的用户名就是邮箱，根据你的实际情况参考)
        user = _get_account_from_email(oauth.id, email, open_id, nickname)

        #登录并跳转
        _login_user(request, user)
        return _bind_success_response(state)

def github_check(request):
    """登录之后，会跳转到这里。需要判断code和state"""
    request_code = request.GET.get('code')
    state = request.GET.get('state') or '/'
    oauth = _get_oauth('Github', state)

    #获取access_token
    try:
        access_token = oauth.get_access_token(request_code)
        time.sleep(0.05)    #稍微休息一下，避免发送urlopen的10060错误
    except Exception as e:
        #登录出错跳转到错误提示页面
        return _login_error_response(e.message, state)

    #获取用户信息
    infos = oauth.get_user_info()
    open_id = str(infos.get('id', ''))
    nickname = infos.get('login', '')

    #检查id是否存在
    githubs = OAuth_ex.objects.filter(openid = open_id, oauth_type = oauth.id)

    #获取邮箱
    if githubs:
        #存在则获取对应的用户，并登录
        _login_user(request, githubs[0].user)
        return HttpResponseRedirect(state)
    else:
        #不存在，则尝试获取邮箱
        try:
            #获取得到邮箱则直接绑定
            email = oauth.get_email()
        except Exception as e:
            #获取不到即跳转到绑定用户
            return _bind_email_response(open_id, nickname, oauth.oauth_type, state)

        #获取到邮箱，直接绑定
        #判断是否存在对应的用户(我这里的用户名就是邮箱，根据你的实际情况参考)
        user = _get_account_from_email(oauth.id, email, open_id, nickname)

        #登录并跳转
        _login_user(request, user)
        return _bind_success_response(state)

def bind_email(request):
    open_id = request.GET.get('open_id')
    nickname = request.GET.get('nickname')
    oauth_type = request.GET.get('oauth_type')
    state = request.GET.get('state') or '/'
    data = {}

    #判断oauth类型
    oauth_types = OAuth_type.objects.filter(type_name = oauth_type)
    if oauth_types.count() > 0:
        oauth_type = oauth_types[0]
        img_url = oauth_type.img
    else:
        data['goto_url'] = state
        data['goto_time'] = 3000
        data['goto_page'] = True
        data['message'] = u'错误的登录类型，请检查'
        return render_to_response('message.html',data)
    
    data['form_title'] = u'绑定用户'
    data['submit_name'] = u'　确定　'
    data['form_tip'] = u'Hi, <span class="label label-info"><img src="/%s">%s</span>！您已登录。请绑定用户，完成登录' % (img_url, nickname)

    if request.method == 'POST':
        #表单提交
        form = BindEmail(request.POST)
        
        #验证是否合法
        if form.is_valid():
            #判断邮箱是否注册了
            openid = form.cleaned_data['openid']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['pwd']

            users = User.objects.filter(email = email)
            if users:
                #用户存在，则直接绑定
                user = users[0]
                if not user.first_name:
                    user.first_name = nickname    #更新昵称
                    user.save()
                data['message'] = u'绑定账号成功，绑定到%s”' % email
            else:
                #用户不存在，则注册，并发送激活邮件
                user=User(username=email, email=email)
                user.first_name = nickname #使用第三方账号昵称作为昵称
                user.set_password(pwd)
                user.is_active=True #激活，此处也可以不用先激活。发送一个邮件确认用户身份，再激活
                user.save()

                data['message'] = u'绑定账号成功'

            #绑定用户
            oauth_ex = OAuth_ex(user = user, openid = openid, oauth_type = oauth_type)
            oauth_ex.save()
            
            #登录用户
            user = authenticate(username=email, password=pwd)
            if user is not None:
                login(request, user)

            #页面提示
            data['goto_url'] = state
            data['goto_time'] = 3000
            data['goto_page'] = True
            
            return render_to_response('message.html',data)
    else:
        #正常加载
        form = BindEmail(initial={
            'openid': open_id,
            'nickname': nickname,
            'oauth_type_id': oauth_type.id,
            })
    data['form'] = form
    return render(request, 'form.html', data)
