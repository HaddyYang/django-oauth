#coding:utf-8
from django.db import models

#若不是使用系统的用户认证，可以换成你自己的用户系统
from django.contrib.auth.models import User 

class OAuth_type(models.Model):
    """OAuth类型"""
    type_name = models.CharField(max_length = 12)
    title = models.CharField(max_length = 12)
    #图片上传的路径可以修改成自己的
    img = models.FileField(upload_to='static/img/connect') 

    #oauth基本设置
    client_id = models.CharField(max_length = 24, default='')
    client_secret = models.CharField(max_length = 48, default='')
    redirect_uri = models.URLField(default='')
    scope = models.CharField(max_length = 24, default='')

    #oauth请求链接
    url_authorize = models.URLField(default='', blank=True)
    url_access_token = models.URLField(default='', blank=True)
    url_open_id = models.URLField(default='', blank=True)
    url_user_info = models.URLField(default='', blank=True)
    url_email = models.URLField(default='', blank=True)

    def __unicode__(self):
        return self.type_name

class OAuth_ex(models.Model):
    """User用户绑定"""
    user = models.ForeignKey(User)   #和User关联的外键
    openid = models.CharField(max_length = 64) 
    oauth_type = models.ForeignKey(OAuth_type, default=1)  #关联账号的类型

    def __unicode__(self):
        return u'<%s>' % (self.user)
