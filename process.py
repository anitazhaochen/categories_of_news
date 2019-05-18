#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo
from sklearn.externals import joblib
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import jieba

class util(object):

    def __init__(self):
        pass

    def category(self):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.yyj
        result = db.sina_test.find()
        for record in result:
            url_1 = record['url']
            cate = url_1.split('.')[0]
            cate = cate.split(":")
            cate = cate[1][2:]
            record['category'] = cate
            print(cate)
            db.sina_add_url_test.insert_one(record)

    def savemodel(self,model):
        # 保存模型到 model.joblib 文件
        joblib.dump(model, "model.joblib", compress=1)

    def load_model(self,path):
        classifier = joblib.load(path)
        return classifier

    def wordcloud(self, words_count):
        matplotlib.rcParams['figure.figsize'] = (10.0,5.0)
        wordcloud = WordCloud(font_path = "./data/simfang.ttf",
                       background_color="white", max_font_size=80)
        word_frequence = {x[0]:x[1] for x in words_count.head(100).values}
        wordcloud = wordcloud.fit_words(word_frequence)
        plt.imshow(wordcloud)
        # 输出词云图片
        plt.show()

    def getdata(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['yyj']
        pk10 = db['sina_add_url']
        df_news = pd.DataFrame(list(pk10.find()))
        del df_news['_id']
        df_news.dropna()
        df_news = df_news[['title', 'url', 'content', 'category']]
        print(len(df_news))
        content = df_news.content.values.tolist()
        content_S = []
        category_S = []
        for line in range(len(content)):
            current_segment = jieba.lcut(content[line])
            if len(current_segment) > 1 and current_segment != '\r\n':
                category_S.append(df_news['category'][line])
                content_S.append(current_segment)
        return content_S, category_S

if __name__ == "__main__":
    u = util()
    u.category()