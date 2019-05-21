#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import jieba
import pymongo
import pandas as pd
import numpy
import process

u = process.util()
content_S, category_S = u.getdata()

df_content = pd.DataFrame({"content_S": content_S})
print(df_content.head())

# 清除停用词
contents_clean, all_words = u.clean_stopwords(df_content.content_S.values.tolist(), 'baidu_stopwords.txt')
#print(contents_clean[0])
#print(len(contents_clean))
df_content = pd.DataFrame({'contents_clean':contents_clean})
#print(df_content.head())
df_all_words = pd.DataFrame({"all_words": all_words})
#print(df_all_words.head())
words_count = df_all_words.groupby(by=['all_words'])['all_words'].agg({"count":numpy.size})
words_count = words_count.reset_index().sort_values(by=["count"],
                                                    ascending=False)

print(words_count.head())

# 输出词云
u.wordcloud(words_count)

## 基于 TF-IDF 提取关键词
u.get_main_key(content_S)

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
                         'label':category_S})
#print(df_train.tail())
#print(df_train.label.unique())
label_mapping = {'news':1, 'finance':2,'tech':3,'sports':4}
df_train['label'] = df_train['label'].map(label_mapping)
print("222222222222")
print(df_train.head())
print("222222222222")

from sklearn.model_selection import train_test_split

print("3333333")
#print(len(df_train))
df_train.dropna(axis=0,how='any',inplace=True)
#print(len(df_train))
print("3333333")


x_train, x_test, y_train, y_test = train_test_split(df_train['contents_clean'].values,
                                           df_train['label'].values,random_state=1)

words = []
for line_index in range(len(x_train)):
    try:
        words.append(' '.join(x_train[line_index]))
    except:
        print(line_index)
print(words[0])
print("关键字数量:   "+str(len(words)))

from sklearn.feature_extraction.text import CountVectorizer

vec = CountVectorizer(analyzer='word', max_features=4000, lowercase = False)
vec.fit(words)

from sklearn.naive_bayes import MultinomialNB
classifier = MultinomialNB()

print(classifier.fit(vec.transform(words), y_train))
test_words = []
print(len(x_test))
for line_index in range(len(x_test)):
    try:
        test_words.append(' '.join(x_test[line_index]))
    except :
        print(line_index)
print(classifier.score(vec.transform(test_words), y_test))
u.savemodel(classifier)

# 预测结果
models = u.load_model("model.joblib")
result = models.predict(vec.transform(words))
for x in result:
    if x == 1:
        print("生活")
    if x == 2:
        print("金融")
    if x == 3:
        print("科技")
    if x == 4:
        print("体育")

