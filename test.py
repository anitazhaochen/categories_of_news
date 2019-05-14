#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import jieba
import pymongo
import pandas as pd
import numpy

client = pymongo.MongoClient('localhost',27017)
db  = client['yyj']
pk10 = db['sina_test']
df_news = pd.DataFrame(list(pk10.find()))
del df_news['_id']
df_news.dropna()
df_news = df_news[['title','url','content']]
#print(len(df_news))
content = df_news.content.values.tolist()
content_S = []
for line in content:
    current_segment = jieba.lcut(line)
    if len(current_segment) > 1 and current_segment != '\r\n':
        content_S.append(current_segment)
#print(content_S[0])

df_content = pd.DataFrame({"content_S": content_S})
#print(df_content.head())

#stopwords = pd.read_csv('./baidu_stopwords.txt', index_col=False, sep='\n',names=['stopword'],header=None)
#stopwords = pd.read_fwf('./baidu_stopwords.txt')
stopwords = pd.read_csv('./baidu_stopwords.txt', sep="\n", header=None,
                        names=["stopword"])

def clean_stopwords(contents, stopwords):
    contents_clean = []
    all_words = []
    for line in contents:
        line_clean = []
        for word in line:
            if word in stopwords:
                #print(word)
                continue
            line_clean.append(word)
            all_words.append(str(word))
        contents_clean.append(line_clean)
    return contents_clean, all_words


contents_clean, all_words = clean_stopwords(df_content.content_S.values.tolist(), stopwords.stopword.values.tolist())
print(contents_clean[0])
df_content = pd.DataFrame({'contents_clean':contents_clean})
#print(df_content.head())
df_all_words = pd.DataFrame({"all_words": all_words})
#print(df_all_words.head())
words_count = df_all_words.groupby(by=['all_words'])['all_words'].agg({"count":numpy.size})
words_count = words_count.reset_index().sort_values(by=["count"],
                                                    ascending=False)
print(words_count.head())

## 词云部分
from wordcloud import WordCloud
import matplotlib.pyplot as plt
#%matplotlib inline
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0,5.0)

wordcloud = WordCloud(font_path = "./data/simfang.ttf",
                       background_color="white", max_font_size=80)

word_frequence = {x[0]:x[1] for x in words_count.head(100).values}
wordcloud = wordcloud.fit_words(word_frequence)
plt.imshow(wordcloud)
# 输出词云图片
#plt.show()

## 基于 TF-IDF 提取关键词
import jieba.analyse
index = 0
print(df_news['content'][index])
content_S_str = ''.join(content_S[index])
print(" ".join(jieba.analyse.extract_tags(content_S_str, topK=5,
                                          withWeight=False)))

## LDA 主题模型
from gensim import corpora, models, similarities
import gensim

# 做映射，相当于词袋
dictionary = corpora.Dictionary(contents_clean)
corpus = [dictionary.doc2bow(sentence) for sentence in contents_clean]
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
                                      num_topics=20)
print(lda.print_topic(1, topn=5))
# 打印 20 个分类的关键词
for topic in lda.print_topics(num_topics=5, num_words=5):
    print(topic[1])
## 基于贝叶斯算法进行分类
df_train = pd.DataFrame({'contents_clean': contents_clean,
                         'label':df_news['category']})
print(df_train.tail())
