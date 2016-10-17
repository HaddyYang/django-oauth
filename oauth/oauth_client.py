#coding:utf-8
import json
import urllib, urllib2, urlparse
import re

class OAuth_Base():
    def __init__(self, kw):
        if not isinstance(kw, dict):
            raise Exception("arg is not dict type")
            
        for key, value in kw.items():
            setattr(self, key, value)

    @staticmethod
    def Get_OAth(**kw):
        """静态方法，根据参数实例化对应的类"""
        type_name = kw.get('type_name')

        if type_name == "QQ":
            oauth = OAuth_QQ(kw)
        elif type_name == "Sina":
            oauth = OAuth_Sina(kw)
        elif type_name == "Github":
            oauth = OAuth_Github(kw)
        else:
            oauth = None
        return oauth

    def _get(self, url, data):
        """get请求"""
        request_url = '%s?%s' % (url, urllib.urlencode(data))
        response = urllib2.urlopen(request_url)
        return response.read()

    def _post(self, url, data):
        """post请求"""
        request = urllib2.Request(url, data = urllib.urlencode(data))
        response = urllib2.urlopen(request)
        return response.read()

    #根据情况重写以下方法
    def get_auth_url(self):
        """获取授权页面的网址"""
        params = {'client_id': self.client_id,
                  'response_type': 'code',
                  'redirect_uri': self.redirect_uri,
                  'scope': self.scope,
                  'state': self.state}
        return '%s?%s' % (self.url_authorize, urllib.urlencode(params))

    #继承的类要实现下面的方法
    def get_access_token(self, code):
        """根据code获取access_token"""
        pass

    def get_open_id(self):
        """获取用户的标识ID"""
        pass

    def get_user_info(self):
        """获取用户资料信息"""
        pass

    def get_email(self):
        """获取邮箱"""
        pass

class OAuth_QQ(OAuth_Base):
    def get_access_token(self, code):
        """根据code获取access_token"""
        params = {'grant_type': 'authorization_code',
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': code,
                  'redirect_uri': self.redirect_uri}
        response = self._get(self.url_access_token, params)

        #解析结果
        if response[:8] == 'callback':
            v_str = str(response)[9:-3] #去掉callback的字符
            v_json = json.loads(v_str)
            raise Exception(v_json['error_description'])
        else:
            result = urlparse.parse_qs(response, True)
            self.access_token = str(result['access_token'][0])
            return self.access_token

    def get_open_id(self):
        """获取QQ的OpenID"""
        params = {'access_token': self.access_token}
        response = self._get(self.url_open_id, params)

        #去掉callback的字符
        result = json.loads(str(response)[9:-3] )
        self.openid = result['openid']
        return self.openid

    def get_user_info(self):
        """获取QQ用户的资料信息"""
        params = {'access_token': self.access_token,
                  'oauth_consumer_key': self.client_id,
                  'openid': self.openid}
        response = self._get(self.url_user_info, params)
        return json.loads(response)

    def get_email(self):
        """获取邮箱"""
        #QQ没有提供获取邮箱的方法
        raise Exception('can not get email')

class OAuth_Sina(OAuth_Base):
    def get_access_token(self, code):
        """根据code获取access_token"""
        params = {'grant_type': 'authorization_code',
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': code,
                  'redirect_uri': self.redirect_uri}

        #新浪微博此处是POST请求，返回JSON
        response = self._post(self.url_access_token, params)
        result = json.loads(response)

        self.access_token = result["access_token"]
        self.openid = result['uid']
        return self.access_token

    def get_open_id(self):
        """获取Sina的uid，由于登录时就获取了，直接返回即可"""
        return self.openid

    def get_user_info(self):
        """获取用户资料信息"""
        params = {'access_token': self.access_token,
                  'uid': self.openid}
        response = self._get(self.url_user_info, params)
        return json.loads(response)

    def get_email(self):
        """获取邮箱"""
        #高级接口，需要申请
        params = {"access_token": self.access_token}
        response = self._get(self.url_email, params)
        #return response

        #分析结果，获取邮箱成功返回是一个字典数组，而不成功则是一个字典
        result = json.loads(response)

        #判断返回数据的类型
        if isinstance(result, list):
            #获取并判断邮箱格式是否正确
            email = result[0].get('email')
            pattern = re.compile(r'^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$')
            match = pattern.match(email)

            if not match:
                raise Exception(u"email format error")
            return email

        elif isinstance(result, dict):
            raise Exception(result.get('error', 'get email happened error'))
        else:
            raise Exception('get email api error')

class OAuth_Github(OAuth_Base):
    openid = ''

    def get_access_token(self, code):
        params = {'grant_type': 'authorization_code',
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': code,
                  'redirect_uri': self.redirect_uri}

        #Github此处是POST请求
        response = self._post(self.url_access_token, params)
        
        #解析结果
        result = urlparse.parse_qs(response, True)
        self.access_token = result['access_token'][0]
        return self.access_token

    def get_open_id(self):
        """获取用户的标识ID"""
        if not self.openid:
            #若没有openid，则调用一下获取用户信息的方法
            self.get_user_info()

        return self.openid

    def get_user_info(self):
        """获取用户资料信息"""
        params = {'access_token': self.access_token,}
        response = self._get(self.url_user_info, params)

        result = json.loads(response)
        self.openid = result.get('id', '')
        return result

    def get_email(self):
        """获取邮箱"""
        params = {'access_token': self.access_token,}
        response = self._get(self.url_email, params)

        result = json.loads(response)
        return result[0]['email']
