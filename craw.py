            #!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import time
import pymongo
import redis



MAIN_URL = "https://news.sina.com.cn/roll/#pageid=153&lid=2509&k=&num=50&page=1";

headers = {'Accept': '*/*',
                'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,ko;q=0.6",
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
               'Referer': 'http://www.baidu.com/'
               }

def get_url_and_title(page=1, timestamp=1556788864475):
    post_url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page="\
           +str(page)+"&r=0.21028240536879106&callback=jQuery1112019530749514224044_1556788864472&_="\
           +str(timestamp)
    s = requests.session()
    s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    s.headers['Accept-Encoding'] = 'gzip, deflate, br'
    s.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,ko;q=0.6'
    s.headers[
        'User-Agent'] = 'zilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    response = s.get(url=post_url)
    #response = requests.get(url=post_url,headers=headers)
    response.encoding = 'utf-8'
    html = response.content.decode("utf-8")
    urls = re.findall(r'\"urls\":\"\[.*?\]\"', html)
    #result2 = re.findall(r'\"url\":\".*?\"', html)
    #result3 = re.findall(r'\"wapurls\":\"\[.*?\]\"', html)
    #result4 = re.findall(r'\"wapurl\":\".*?\"', html)
    titles = re.findall(r'\"title\":\".*?\"', html)
    return urls, titles
    # print(urls)
    # print(titles)
    # di = {}
    # for i in range(len(urls)):
    #     di["title"] = titles[i]
    #     di["url"] = urls[i]

    #print(result2)
    #print(result3)
    #print(result4)
    #print(len(result1))
    #print(len(result2))
    #print(len(result3))
    #print(len(result4))

def process_url_and_title(urls, titles):
    newurl = []
    for url in urls:
        url = url[11:-3]
        url = str.replace(url, "\\", "")
        newurl.append(url)

    newtitles = []
    for title in titles:
        try:
            title = str(titles[0][9:-1]).encode().decode('unicode-escape').encode('utf-8').decode('utf-8') # 反斜杠转义，无法直接转成 utf-8 的汉字
        except:
            print("转义出现错误.. error")
            print(title)
        newtitles.append(title)

    title_and_url = []
    for i in range(len(newtitles)):
        di = {}
        di["title"] = newtitles[i]
        di["url"] = newurl[i]
        title_and_url.append(di)
    return title_and_url

def get_page(title_and_url):

    for di in title_and_url:
        time.sleep(2)
        html = requests.get(di["url"], headers=headers).content
        tree = etree.HTML(html)
        content = tree.xpath('//*[@id="article"]/p/text()')
        if len(content) == 0:
            print("尝试使用另一种xpath")
            content = tree.xpath('//*[@id="artibody"]/p/text()')
            if len(content) == 0:
                print("error    "+di["url"])
        else:
            print("".join(content))
        di["content"] = "".join(content)
    return title_and_url
i = 1

def savetomongo(title_and_url_and_content):
    global i
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.yyq
    sina_col = db.sina
    for data in title_and_url_and_content:
        sina_col.insert_one(data)
        i = i + 1
        print("第" + str(i) + "   条插入成功")

pool = redis.ConnectionPool(host='localhost', port=6379,decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
r = redis.Redis(connection_pool=pool)
def update_page(page):
    global r
    r.set('pageCount', page)  # key是"gender" value是"male" 将键值对存入redis缓存

def get_current_page_count():
    global r
    page = r.get('pageCount')
    return int(page)



def main():
    timestamp = 1556788864476
    page = get_current_page_count()
    while page<=16225:
            urls, titles = get_url_and_title(page, timestamp)
            title_and_urls = process_url_and_title(urls, titles)
            result = get_page(title_and_urls)
            time.sleep(60)
            savetomongo(result)
            print("抓取到第"+str(page)+"页！！！！！！！！！！！")
            page += 1
            timestamp += page
            update_page(page)


if __name__ == "__main__":
    for i in range(10):
        try:
            main()
        except Exception:
            print("请求超时第"+str(i)+   "次")
            time.sleep(60)
