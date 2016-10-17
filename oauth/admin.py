#coding:utf-8
from django.contrib import admin
from .models import OAuth_type, OAuth_ex

# Register your models here.
class OAuthTypeAdmin(admin.ModelAdmin):
    list_display=('id','type_name', 'title', 'img')

    #分组表单
    fieldsets = (
        (u'OAuth类型信息', {
            "fields":('type_name', 'title', 'img')
            }),
        (u'OAuth基本设置', {
            "fields":('client_id','client_secret','redirect_uri','scope')
            }),
        (u'OAuth请求链接', {
            "fields":('url_authorize','url_access_token','url_open_id','url_user_info','url_email')
            })
    )

class OAuthAdmin(admin.ModelAdmin):
    list_display=('id', 'user', 'openid','oauth_type')

admin.site.register(OAuth_ex, OAuthAdmin)
admin.site.register(OAuth_type, OAuthTypeAdmin)
