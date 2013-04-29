#!/bin/env python
# -*- coding: utf-8 -*- 
import hashlib,time,urllib2,soup,sys
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template

reload(sys)
sys.setdefaultencoding('utf-8')
APP_SECRET_KEY = "h12mw5555ly31z3zx5w3435yh0k32mjyw4yiyl5l"

app = Flask(__name__)
app.debug = True
app.secret_key = APP_SECRET_KEY

#homepage just for fun
@app.route('/')
def home():
    return render_template('index.html')

#公众号消息服务器网址接入验证
#需要在公众帐号管理台手动提交, 验证后方可接收微信服务器的消息推送
@app.route('/weixin', methods=['GET'])
def weixin_access_verify():
    echostr = request.args.get('echostr')
    
    if verification(request) and echostr is not None:
        return echostr
    return 'access verification fail'

#来自微信服务器的消息推送
@app.route('/weixin', methods=['POST'])
def weixin_msg():
    data = request.data
    msg = parse_msg(data)
    if user_subscribe_event(msg):
        return help_info(msg)
    elif is_text_msg(msg):
        content = msg['Content']
        if content == u'?' or content == u'？':
            return help_info(msg)
        else:
            return lotterys(msg, content)
    return 'message processing fail'

#接入和消息推送都需要做校验
def verification(request):
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    
    token = 'yiriyiv' #注意要与微信公众帐号平台上填写一致
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = ''.join('%s' % x for x in tmplist)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    
    if hashstr == signature:
        return True
    return False

#将消息解析为dict
def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

def is_text_msg(msg):
    return msg['MsgType'] == 'text'

def user_subscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'subscribe'

HELP_INFO = \
u"""
欢迎关注一日一V^_^
每天进步一点点
"""

def help_info(msg):
    return response_text_msg(msg, HELP_INFO)

TEXT_MSG_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""

def response_text_msg(msg, content):
    s = TEXT_MSG_TPL % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), content)
    return s

def lotterys(msg,content):
    baseurl = u"http://baidu.lecai.com/lottery/draw"
    lottery = soup.soup(baseurl)
    foundTrs = lottery.findAll("tr",{"class":"bgcolor"})
    for tr in foundTrs:
        foundTds = tr.findAll("td")
        if content == foundTds[0].string:
            title = foundTds[0].string
            qishu = foundTds[1].string
            opentime = foundTds[2].string
            foundSpans = tr.findAll("span")
            span = "-".join([i.string for i in foundSpans])
            contents = u"彩种:%s\n期号:%s\n开奖时间:%s\n开奖号码:%s\n" % (title,qishu,opentime,span)
            return response_text_msg(msg,contents)
    return help_info(msg)

if __name__ == '__main__':
    app.run()