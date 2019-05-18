#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo
from sklearn.externals import joblib
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import jieba
import jieba.analyse

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
        sina_data = db['sina_add_url']
        df_news = pd.DataFrame(list(sina_data.find()))
        del df_news['_id']
        print("修改前数据总长度为：")
        print(len(df_news))
        # 删除无用的行！！ 注意 默认返回的是修改后的, inplace 表示在原来的上面修改
        df_news.dropna(axis=0,how="any",inplace=True)
        df_news = df_news[['title', 'url', 'content', 'category']]
        print("数据总长度为：")
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

    def clean_stopwords(self, contents, stopwords):
        contents_clean = []
        all_words = []
        for line in contents:
            line_clean = []
            for word in line:
                if word in stopwords or word == ' ':
                    # print(word)
                    continue
                line_clean.append(word)
                all_words.append(str(word))
            contents_clean.append(line_clean)
        return contents_clean, all_words

    # 基于 TF-IDF 提取关键词
    def get_main_key(self,content_S):
        index = 0
        # print(df_news['content'][index])
        content_S_str = ''.join(content_S[index])
        print(" ".join(jieba.analyse.extract_tags(content_S_str, topK=5,
                                                  withWeight=False)))

    def process_mongo_data(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['yyj']
        sina_data = db['sina_add_url']
        result = sina_data.find()
        for r in result:
            if r['content']!='' and r['category'] != '':
                pass
            else:
                print("删除")
                sina_data.delete_one(r)

if __name__ == "__main__":
    u = util()
    u.process_mongo_data()
