# -*- coding:utf-8 -*-  
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs

import scrapy


class WxMessageSpider(scrapy.Spider):
    name = "wx_message"
    allowed_domains = ["qq.com"]

    def __init__(self, url=None, img=False):
        # print url
        self.start_urls = [url]
        self.img = img

    def parse(self, response):
        self.parse_text(response)
        if self.img:
            self.parse_img(response)

    def parse_text(self, response):
        head = response.xpath('//h2[@id="activity-name"]/text()').extract()[0].replace('\n','').replace('\r','').strip()
        ps = response.xpath('//div[@id="img-content"]/div[2]/p')
        content = '\r\n'.join([p.xpath('string(.)').extract()[0] for p in ps])
        time = response.xpath('//em[@id="post-date"]/text()').extract()[0]
        auth = response.xpath('//a[@id="post-user"]/text()').extract()[0]
        text = '\r\n'.join([head,time + ' ' + auth,content])
        file_name = self.filter_file_name(head)
        with codecs.open(file_name + '.txt','w',encoding='utf-8') as f:
            f.write(text)
        print file_name

    def parse_img(self, response):
        head = response.xpath('//h2[@id="activity-name"]/text()').extract()[0].replace('\n','').replace('\r','').strip()
        head = self.filter_file_name(head)
        div = response.xpath('//div[@id="img-content"]/div[2]')
        imgs = div.xpath('.//img[@data-src]/@data-src').extract()
        for num,img in enumerate(imgs):
            self.download_img(img, head+'-'+str(num)+'.jpeg')

    def download_img(self, url, file):
        import urllib2
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat')
        resp = urllib2.urlopen(req)
        with open(file,'wb') as f:
            f.write(resp.read())

    def filter_file_name(self, file_name):
        import re
        import os
        if os.name == 'nt':
            return re.sub(r'\<|\>|\/|\\|\||\:|\"|\*|\?','',file_name)
        else:
            return re.sub(r'\/','',file_name)
