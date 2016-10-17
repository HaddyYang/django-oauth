#django-oauth
<h4>
    <strong>项目说明</strong>
</h4>
<p>
    该项目是django的app应用，主要用途是使用OAuth2.0关联第三方账号。<br/>
</p>
<p>
    鉴于我的django项目是采用django自带的用户认证系统，而且用户名是使用邮箱地址作为用户名。其中有些代码涉及到这两个东西，导致代码通用性一般。
</p>
<p>
    推荐参考其中oauth/oauth_client.py文件即可。
</p>
<p>
    也可以参考我博客：<a href="http://yshblog.com/blog/77" target="_blank">第三方登录整理</a>
</p>
<p>
    在我博客中，也对QQ、Sina、Github的OAuth开发过程中逐个写了博文：
</p>
<p>
    1、<a href="http://yshblog.com/blog/60" target="_blank">QQ第三方登录</a>
</p>
<p>
    2、<a href="http://yshblog.com/blog/68" target="_blank">新浪微博第三方登录</a>
</p>
<p>
    3、<a href="http://yshblog.com/blog/70" target="_blank">Github第三方登录</a>
</p>
<h4>
    <strong>目录说明</strong>
</h4>
<p>
    oauth是实现oauth主要的代码，templates是相关的模版文件(根据自己情况需要修改)
</p>
<p>
    oauth相关设置记录在数据库中，即可以查看oauth/models.py中的OAuth_type设计。
</p>
<h4>
    <strong>使用说明</strong>
</h4>
<p>
    1、复制该应用到你的django项目中。
</p>
<p>
    2、打开settings.py文件，INSTALLED_APP中添加应用 &#39;oauth&#39;
</p>
<p>
    3、打开总的urls.py文件，添加本应用的路由设置
    <pre>url(r'^oauth/',include('apps_project.oauth.urls')),</pre>
</p>
<p>
    4、更新数据库
</p>
<pre>python manage.py makemigrations
python manage.py migrate</pre>
<p>
    5、进入django后台管理，新增OAuth设置（包括回调地址、请求链接等等）
</p>
<p>
    6、测试代码 --&gt; 调试 --&gt; 上线
</p>