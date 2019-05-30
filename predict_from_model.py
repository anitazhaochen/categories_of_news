#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

import process
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import pymongo

u = process.util()
content_S, category_S = u.getdata("sina_add_url_test")
df_content = pd.DataFrame({"content_S": content_S})

contents_clean, all_words = u.clean_stopwords(df_content.content_S.values.tolist(), 'baidu_stopwords.txt')
df_train = pd.DataFrame({'contents_clean': contents_clean,
                         'label':category_S})
#label_mapping = {'news':1, 'finance':2,'tech':3,'sports':4}
#df_train['label'] = df_train['label'].map(label_mapping)
x_test = df_train.contents_clean.values.tolist();
test_words = []
for line_index in range(len(x_test)):
    try:
        test_words.append(' '.join(x_test[line_index]))
    except :
        print(line_index)

feature_path = 'feature.pkl'
vec = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open(feature_path, "rb")))

models = u.load_model("model.joblib")
result = models.predict(vec.transform(test_words))

def verify(pre_result):
    client = pymongo.MongoClient()
    table = client.yyj.sina_add_url_test
    result = table.find()
    label_mapping = {'1':'news' , '2':'finance', '3':'tech' , '4':'sports','5':'mil'}
    result = list(result)
    pre_result = str(pre_result)[1:-1]
    pre_result = pre_result.replace('\n','')
    pre_result = pre_result.split(" ")
    print(pre_result)
    for i in range(len(pre_result)):
        category = label_mapping[str(pre_result[i])]
        pre_result[i] = category
    count = 0
    for i in range(len(result)):
        if result[i]['category'] == pre_result[i]:
            count += 1
            continue
        print("错误分类!!!")
        print("原文")
        print(result[i]['content'])
        print("原本分类为"+ result[i]['category'])
        print("预测分类为" + pre_result[i])
        print("\n\n\n")

    print("本次分类的正确率为")
    print(count*100/50,end="")
    print("%")

verify(result)
