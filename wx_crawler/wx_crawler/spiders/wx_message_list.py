# -*- coding:utf-8 -*-  
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs

import scrapy
from wx_message import WxMessageSpider

class WeixinSpider(scrapy.Spider):
    name = "weixin"
    allowed_domains = ["qq.com"]
    start_urls = (
        'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MjM5MjAxNDM4MA==&uin=MTM4MjQxMDAyMw%3D%3D&key=41ecb04b051110032c7441cbf9ca561cd13ecc01510163d62a95261e623d86b71a064452b41ab4e8b8195008c78ddd2d',
    )

    def __init__(self, img=False):
        self.message_crawler = WxMessageSpider(None, img)

    def parse(self, response):
        json_str = response.body.split("msgList = '")[1].split("'")[0].replace('&quot;','"')
        import json
        json_json = json.loads(json_str)
        lists = json_json['list']
        for item in lists:
            message_id = item['comm_msg_info']['id']
            url = item['app_msg_ext_info']['content_url']
            yield scrapy.Request(url.replace('\\','').replace('amp;amp;','amp;'), callback=self.message_crawler.parse)
            subs = item['app_msg_ext_info']['multi_app_msg_item_list']
            for sub in subs:
                sub_url = sub['content_url']
                yield scrapy.Request(sub_url.replace('\\','').replace('amp;amp;','amp;'), callback=self.message_crawler.parse)
        yield scrapy.Request(response.url.split('&f=text&frommsgid')[0]+"&f=text&frommsgid="+str(message_id)+"&count=10", callback=self.parse)
