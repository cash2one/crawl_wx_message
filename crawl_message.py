# -*- coding:utf-8 -*-  
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from lxml import html
import requests
import codecs
import threading
import re

class Message_crawl(threading.Thread):

    def __init__(self, url, img = False):
        super(Message_crawl, self).__init__()
        self.url = url
        self.img = img

    def crawl_text(self, tree):
        try:
            head = tree.xpath('//h2[@id="activity-name"]/text()')[0]
        except Exception:
            print self.url, '可能不是文章而是美团红包等'
            return
        time = tree.xpath('//em[@id="post-date"]/text()')[0]
        ts = tree.xpath('//div[@id="js_content"]//*[text()]')
        text = '\r\n'.join(t.xpath('text()')[0] for t in ts if len(t.xpath('text()')) and len(t.xpath('text()')[0]))
        file_name = self.filter_file_name(head)
        file_name = time + '_' + file_name + '.txt'
        with codecs.open(file_name,'w',encoding='utf-8') as f:
            f.write(text)
        return file_name

    def crawl_img(self, tree):
        time = tree.xpath('//em[@id="post-date"]/text()')[0]
        head = tree.xpath('//h2[@id="activity-name"]/text()')[0]
        head = self.filter_file_name(head)
        div = tree.xpath('//div[@id="js_content"]')
        imgs = tree.xpath('//div[@id="js_content"]//img[@data-src]/@data-src')
        for num,img in enumerate(imgs):
            self.download_img(img, time + '_' + head+'_'+str(num)+'.jpeg')
        return len(imgs)


    def download_img(self, url, file):
        import urllib2
        req = urllib2.Request(url)
        # req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat')
        resp = urllib2.urlopen(req)
        with open(file,'wb') as f:
            f.write(resp.read())

    def filter_file_name(self, file_name):
        import os
        if os.name == 'nt':
            return re.sub(r'\<|\>|\/|\\|\||\:|\"|\*|\?|\r|\n|\s','',file_name)
        else:
            return re.sub(r'\/|\r|\n|\s','',file_name)

    def run(self):
        if not self.url:
            print '要抓取的url为空'
            return
        resp = requests.get(self.url)
        c = resp.content
        tree = html.fromstring(c)
        head = self.crawl_text(tree)
        if self.img:
            num = self.crawl_img(tree)
            print  self.url,'下抓取到文章：',head,'抓取到',num,'张图片。'
        else:
            print self.url,'下抓取到文章：',head

# windows下编码问题修复
# http://blog.csdn.net/heyuxuanzee/article/details/8442718
class UnicodeStreamFilter:  
    def __init__(self, target):  
        self.target = target  
        self.encoding = 'utf-8'  
        self.errors = 'replace'  
        self.encode_to = self.target.encoding  
    def write(self, s):  
        if type(s) == str:  
            s = s.decode('utf-8')  
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)  
        self.target.write(s)  
          
if sys.stdout.encoding == 'cp936':  
    sys.stdout = UnicodeStreamFilter(sys.stdout)

def main(url):
    m = Message_crawl(url, True)
    # m.setDaemon(True)
    m.start()
    print 'end'

if __name__ == '__main__':
    import sys
    try:
        url = sys.argv[1]
    except Exception:
        print 'usage: python crawl_message.py url'
        sys.exit(-1)
    main(sys.argv[1])

