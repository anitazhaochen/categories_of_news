#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

import pandas as pd
import numpy
import process

u = process.util()
content_S, category_S = u.getdata("sina_add_url")

df_content = pd.DataFrame({"content_S": content_S})
print("原始数据：")
print(df_content.head())
print()
# 清除停用词
print("开始执行清除停用词--------------------")
contents_clean, all_words = u.clean_stopwords(df_content.content_S.values.tolist(), 'baidu_stopwords.txt')

# 重新将已经把停用词清除的 条目 在创建一个数据格式
df_content = pd.DataFrame({'contents_clean':contents_clean})
print("清除停用词后的数据对比")
print(df_content.head())
# 对所有的词通过 pandas 来进行格式化,后期做图云使用
df_all_words = pd.DataFrame({"all_words": all_words})

# 通过 pandas 自带的统计工具，对词语进行词频攻击
words_count = df_all_words.groupby(by=['all_words'])['all_words'].agg({"count":numpy.size})
words_count = words_count.reset_index().sort_values(by=["count"],
                                                    ascending=False)

print("对词频进行排序后输出出现最多的前5个词语")
print(words_count.head())
print()

# 输出词云
u.wordcloud(words_count)


## 基于 TF-IDF 提取关键词
# u.get_main_key(content_S)

## LDA 主题模型
from gensim import corpora, models, similarities
import gensim

# 做映射，相当于词袋
dictionary = corpora.Dictionary(contents_clean)
corpus = [dictionary.doc2bow(sentence) for sentence in contents_clean]
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
                                      num_topics=5)
print("打印前5篇文章通过关键词提取出来的词向量")
print(lda.print_topic(1, topn=5))
# 打印 20 个分类的关键词
for topic in lda.print_topics(num_topics=5, num_words=5):
    print(topic[1])
## 基于贝叶斯算法进行分类
df_train = pd.DataFrame({'contents_clean': contents_clean,
                         'label':category_S})
label_mapping = {'news':1, 'finance':2,'tech':3,'sports':4,'mil':5}
print()
print("数字和所属分类做映射")
print(label_mapping)
print()
df_train['label'] = df_train['label'].map(label_mapping)
print()
print("打印训练集的前 5 篇文章,及所属类别")
print(df_train.head())
print()

from sklearn.model_selection import train_test_split

df_train.dropna(axis=0,how='any',inplace=True)

x_train, x_test, y_train, y_test = train_test_split(df_train['contents_clean'].values,
                                           df_train['label'].values,random_state=1)

words = []
for line_index in range(len(x_train)):
    try:
        words.append(' '.join(x_train[line_index]))
    except:
        print(line_index)
print("打印第一篇文章的中提取出来的 比较重要的关键词,一共", end= " ")
print(str(len(words))+" 个")
print(words[0])
print()

from sklearn.feature_extraction.text import CountVectorizer

vec = CountVectorizer(analyzer='word', max_features=4000, lowercase = False)
vec.fit(words)

feature_path = 'feature.pkl'
with open(feature_path, 'wb') as fw:
    pickle.dump(vec.vocabulary_, fw)

from sklearn.naive_bayes import MultinomialNB
classifier = MultinomialNB()

print(classifier.fit(vec.transform(words), y_train))

test_words = []
for line_index in range(len(x_test)):
    try:
        test_words.append(' '.join(x_test[line_index]))
    except :
        print(line_index)
print("预测准确率为： ", end= " ")
print(classifier.score(vec.transform(test_words), y_test))
print()

u.savemodel(classifier)

# 预测结果
models = u.load_model("model.joblib")
result = models.predict(vec.transform(test_words))
a,b,c,d,e = 0,0,0,0,0
for x in result:
    if x == 1:
        a+= 1
        print("生活",end=" ")
    if x == 2:
        b += 1
        print("金融",end=" ")
    if x == 3:
        c += 1
        print("科技", end=" ")
    if x == 4:
        d += 1
        print("体育",end=" ")
    if x == 5:
        e += 1
        print("军事", end=" ")

print()
print(a)
print(b)
print(c)
print(d)
