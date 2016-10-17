#coding:utf-8
from django.conf.urls import include, url
from .views as oauth_views

#http://localhost:8000/oauth/
#start with 'oauth/'
urlpatterns = [
    url(r'^oauth_login/(?P<type_name>[a-zA-Z]+)$', oauth_views.oauth_login, name='oauth_login'),

    #此处要和第三方账号填写的回调地址对应
    url(r'^qq_check$', oauth_views.qq_check, name='qq_check'),
    url(r'^sina_check$', oauth_views.sina_check, name='sina_check'),
    url(r'^github_check$', oauth_views.github_check, name='github_check'),

    url(r'^bind_email$', oauth_views.bind_email, name='bind_email'),    
]
