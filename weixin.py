# -*- coding:utf-8 -*-  
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import requests
import codecs
import json
import os
import threading
import urllib2

from crawl_message import Message_crawl

class WebWx():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36', 'Origin':'https://wx.qq.com'}#, 'Origin':'https://wx.qq.com'
    deviceid = "e752739129355177"
    localid = "14518913695500856"
    uuid = None
    wxuin = None
    wxsid = None
    scan = None
    ticket = None
    skey = None
    sync = None
    pass_ticket = None
    fname = None
    pub_accounts = {}
    session = requests.Session()

    def get_time(self):
        return str(int(time.time()*1000))
        # return int(time.time()*1000)

    def get_url(self, url):
        return self.session.get(url, headers=self.headers)

    def post_url(self, url, data):
        return self.session.post(url, data=data, headers=self.headers)

    def prepare(self):
        print '准备'
        self.get_url('https://wx.qq.com/')
        self.get_url('https://js.aq.qq.com/js/aq_common.js')
        self.get_url('https://res.wx.qq.com/zh_CN/htmledition/v2/css/base/base28a2f7.css')
        self.get_url('https://res.wx.qq.com/zh_CN/htmledition/v2/js/libs28a2f7.js')
        self.get_url('https://res.wx.qq.com/zh_CN/htmledition/v2/js/webwxApp2aa30f.js')
        self.get_url('https://tajs.qq.com/stats?sId=43209744')
        a=requests.cookies.create_cookie('pgv_pvi','7691603968',domain='.qq.com')
        b=requests.cookies.create_cookie('pgv_si','s7891210240',domain='.qq.com')
        c=requests.cookies.create_cookie('wxpluginkey','1451869344',domain='.wx.qq.com')
        self.session.cookies.set_cookie(a)
        self.session.cookies.set_cookie(b)
        self.session.cookies.set_cookie(c)

    def get_uuid(self):
        print '获取uuid'
        url = 'https://login.weixin.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=' + self.get_time()

        resp = self.get_url(url)
        self.uuid = resp.content.split('"')[1]
        # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
        return self.uuid

    def get_qrcode(self):
        print '获取二维码图片'
        url = 'https://login.weixin.qq.com/qrcode/'+self.uuid

        resp = self.get_url(url)
        with open('qrcode.jpg','wb') as f:
            f.write(resp.content)
        os.system('call qrcode.jpg')
        return None

    def get_login_url(self):
        print '轮询二维码处理状态，获取登录链接'
        url = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?uuid="+self.uuid+"&tip=1&_=" + self.get_time()

        resp = self.get_url(url)
        qrcode_statue = resp.content.split(';')[0]
        while qrcode_statue != 'window.code=200':
            print '手机端未扫描并确认登录'
            resp = self.get_url(url)
            qrcode_statue = resp.content.split(';')[0]
            time.sleep(0.5)
        print '手机端已确认登录'
        os.system('taskkill /f /im dllhost.exe')
        os.remove('qrcode.jpg')
        login_url = resp.content.split('"')[1]+'&fun=new&version=v2&lang=zh_CN'
        self.ticket = login_url.split('ticket=')[1].split('&')[0]
        self.scan = login_url.split('scan=')[1].split('&')[0]
        return login_url

    def get_uin_sid(self, login_url):
        print "访问登录链接，获取uin、sid、skey、pass_ticket"
        resp = self.get_url(login_url)

        self.uin = self.session.cookies['wxuin']
        self.sid = self.session.cookies['wxsid']
        self.skey = resp.content.split('skey>')[1][:-2]
        self.pass_ticket = resp.content.split('pass_ticket>')[1][:-2]
        return (self.uin, self.sid, self.skey, self.pass_ticket)

    def report(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatreport?fun=new'
        data = {"BaseRequest":{"Uin":self.uin,"Sid":""},"Count":0,"List":[]}
        self.post_url(url, data)

    def init_wx(self):
        print '初始化微信'
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?pass_ticket=%s&skey=%s&r=%s'%(self.pass_ticket,self.skey,self.get_time())
        data = {
            "BaseRequest":{
                "Uin":self.uin,
                "Sid":self.sid,
                "Skey":self.skey,
                "DeviceID":self.deviceid
            }
        }
        request = urllib2.Request(url = url, data = json.dumps(data))
        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib2.urlopen(request)
        data = response.read()
        json_data = json.loads(data)
        self.sync = json_data['SyncKey']
        self.fname = json_data['User']['UserName']
        MPSubscribeMsgList = json_data['MPSubscribeMsgList']
        for MPSubscribeMsg in MPSubscribeMsgList:
            MPArticleList = MPSubscribeMsg['MPArticleList']
            for MPArticle in MPArticleList:
                t = Message_crawl(MPArticle['Url'])
                t.start()

    def get_contact(self):
        print '获取联系人'
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket='+self.pass_ticket+'&r='+self.get_time()+'3&seq=0&skey='+self.skey
        resp = self.get_url(url)
        with codecs.open('contact.json','w',encoding='utf-8') as f:
            f.write(resp.content)
        contacts = json.loads(resp.content)['MemberList']
        print '好友人数：%d'%(len(contacts))

        SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
        for member in contacts:
            if member['VerifyFlag'] & 8 != 0: # 公众号/服务号
                self.pub_accounts[member['UserName']] = member['NickName']
        print '公众号数量：%d'%(len(self.pub_accounts))
        return None

    def notify(self):
        print "notify"
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?pass_ticket='+self.pass_ticket
        data={"BaseRequest":{"Uin":self.uin,"Sid":self.sid,"Skey":self.skey,"DeviceID":self.deviceid},"Code":3,"FromUserName":self.fname,"ToUserName":self.fname,"ClientMsgId":self.localid}
        resp = self.post_url(url,data)
        print resp.content
        return json.loads(resp.content)['MsgID']

    def send_message(self):
        print '发送消息'
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?pass_ticket='+self.pass_ticket
        data = {
            "BaseRequest":{
                "Uin":int(self.uin),
                "Sid":self.sid,
                "Skey":self.skey,
                "DeviceID":self.deviceid
            },
            "Msg":{
                "Type":1,
                "Content":"test",
                "FromUserName":self.fname,
                "ToUserName":self.wangao,
                "LocalID":self.localid,
                "ClientMsgId":self.localid
            }
        }

        resp = self.post_url(url, data)
        print resp.content
        return None

    def formate_rsync(self,json_rsync):
        l = json_rsync['List']
        sl = []
        for i in l:
            sl.append(str(i['Key'])+'_'+str(i['Val']))
        s = '%'.join(sl)
        return s

    def sync_check(self):
        while 1:
            t = self.get_time()
            url = 'https://webpush.weixin.qq.com/cgi-bin/mmwebwx-bin/synccheck?r='+t+'&skey'+self.skey+'&sid='+self.sid+'&uin='+self.uin+'&deviceid='+self.deviceid+'&synckey='+self.formate_rsync(self.sync)+'&_='+t
            resp = self.get_url(url)
            # window.synccheck={retcode:"0",selector:"0"}
            retcode = resp.content.split('"')[1]
            selector = resp.content.split('"')[3]
            # print resp.content
            # while retcode=='0' and selector=='0':
            #     print '暂无消息'
            #     time.sleep(5)
            #     resp = self.get_url(url)
            #     retcode = resp.content.split('"')[1]
            #     selector = resp.content.split('"')[3]
            if int(retcode):
                print '同步消息出错：', resp.content
                break
            if selector!='0':
                self.get_sync(selector)
                # break


    def get_sync(self, selector):
        # print '尝试处理新消息'
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid='+self.sid+'&skey='+self.skey+'&lang=zh_CN&pass_ticket='+self.pass_ticket
        data = {
            "BaseRequest" : {
                "Uin":self.uin,
                "Sid":self.sid
            },
            "SyncKey" : self.sync,
            "rr" : int(time.time())
        }
        request = urllib2.Request(url = url, data = json.dumps(data))
        request.add_header('ContentType', 'application/json; charset=UTF-8')
        response = urllib2.urlopen(request)
        data = response.read()
        json_data = json.loads(data)
        # print json_data
        self.sync = json_data['SyncKey']
        if selector == '6':
            new_messages = json_data['AddMsgList']
            for new_message in new_messages:
                from_user = new_message['FromUserName']
                url = new_message['Url']
                if from_user in self.pub_accounts:
                    if url:
                        print '收到来自',self.pub_accounts[from_user],'的文章：',url
                        t = Message_crawl(url)
                        t.start()
        return


    def run(self):
        # self.prepare()
        self.get_uuid()
        self.get_qrcode()
        login_url = self.get_login_url()
        self.get_uin_sid(login_url)
        self.init_wx()
        self.get_contact()
        self.sync_check()

def main():
    wx = WebWx()
    wx.run()

if __name__ == '__main__':
    main()



