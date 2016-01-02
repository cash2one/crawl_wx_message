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
        'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzA4NDc2MTU2MQ==&uin=MTM4MjQxMDAyMw%3D%3D&key=41ecb04b05111003cb78720b68e2b4ff833b77e0c977681ceaf426c1f23fc304c83b9a7c4639e26c8c1833a6f6afa770&devicetype=Windows+7&version=61050021&lang=zh_CN&pass_ticket=daiVwVElSpDwTDJSMxOab7UIAeptN40pVSbMtGX%2BTrrvasGi7lpjzCnsBE9Uvuh3 HTTP/1.1',
    )

    def __init__(self, img=False):
        self.message_crawler = WxMessageSpider(None, img)

    def parse(self, response):
    	json_str = response.body.split("msgList = '")[1].split("'")[0].replace('&quot;','"')
    	import json
    	json_json = json.loads(json_str)
    	lists = json_json['list']
    	for item in lists:
    		url = item['app_msg_ext_info']['content_url']
    		yield scrapy.Request(url.replace('\\','').replace('amp;amp;','amp;'), callback=self.message_crawler.parse)
    		subs = item['app_msg_ext_info']['multi_app_msg_item_list']
    		for sub in subs:
    			sub_url = sub['content_url']
    			yield scrapy.Request(sub_url.replace('\\','').replace('amp;amp;','amp;'), callback=self.message_crawler.parse)


    # def parse_text(self, response):
    # 	head = response.xpath('//h2[@id="activity-name"]/text()').extract()[0].replace('\n','').replace('\r','').strip()
    #     ps = response.xpath('//div[@id="img-content"]/div[2]/p')
    #     content = '\r\n'.join([p.xpath('string(.)').extract()[0] for p in ps])
    #     time = response.xpath('//em[@id="post-date"]/text()').extract()[0]
    #     auth = response.xpath('//a[@id="post-user"]/text()').extract()[0]
    #     text = '\r\n'.join([head,time + ' ' + auth,content])
    #     with codecs.open(head+'.txt','w',encoding='utf-8') as f:
    #     	f.write(text)
    #     #下方print语句在linux下没问题，但是在windows下会有编码问题
    #     #print head
