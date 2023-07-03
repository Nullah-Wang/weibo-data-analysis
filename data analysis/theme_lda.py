import jieba
import jieba.analyse
import numpy as np
import pandas as pd
import re
from gensim import corpora, models, similarities
import gensim

# =====1.加载数据===========
filename = "theme_jieba.csv"
pd.set_option('max_colwidth', 500)      # pd默认最大值为50
df = pd.read_csv(filename, usecols=['contents_clean','biaoqian'], encoding='gbk')

df.dropna(axis=0, subset=['contents_clean'])     # 丢弃评论为缺失值的行

contents_clean = df.contents_clean.values.tolist()
biaoqian = df.biaoqian.values.tolist()

# # =====4.TF-IDF提取关键词===========
# index = 0#取第几行
# print(df['content'][index])
# content_S_str = "".join(content_S[index])#把这一行的主要关键字给取出来
# # print(content_S_str)
# print("  ".join(jieba.analyse.extract_tags(content_S_str, topK=5, withWeight=False)))


#做映射，相当于词袋
dictionary = corpora.Dictionary([contents_clean])
corpus = [dictionary.doc2bow(sentence) for sentence in [contents_clean]]
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=20) #类似Kmeans自己指定K值
#一号分类结果
# print (lda.print_topic(1, topn=5))


# for topic in lda.print_topics(num_topics=20, num_words=5):
#     print(topic[1])
df_train = pd.DataFrame({'contents_clean': contents_clean, 'label': biaoqian})#
# print(df_train.tail())
# print(df_train.label.unique())


# label替换，映射成数字。   其实数据中并没有label
label_mapping = {"好": 3, "坏": 4}
df_train['label'] = df_train['label'].map(label_mapping)
print(df_train.head())


# 划分训练集，测试集
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(df_train['contents_clean'].values,df_train['label'].values,  random_state=1)#
# print(x_train[0][1])

# 主要是把列表转成字符串，  (' '.join(x_train[line_index]))作用是把列表转化为字符串
words = []
for line_index in range(len(x_train)):
    try:
        # x_train[line_index][word_index] = str(x_train[line_index][word_index])
        words.append(''.join(x_train[line_index]))
    except:
        print(line_index)

print(words[0])#相当于一篇文章
print(len(words))


# 用CountVectorizer构造向量生成
from sklearn.feature_extraction.text import CountVectorizer
vec = CountVectorizer(analyzer='word', max_features=4000,  lowercase = False)
vec.fit(words)
# 导入贝叶斯，fit进vec.transform(words)输入特征和标签y_train
from sklearn.naive_bayes import MultinomialNB
classifier = MultinomialNB()

print(y_train)

classifier.fit(vec.transform(words), y_train)

# # 用CountVectorizer构造向量生成
# from sklearn.feature_extraction.text import TfidfVectorizer
# vectorizer = TfidfVectorizer(analyzer='word', max_features=4000,  lowercase = False)
# vectorizer.fit(words)
#
# # 导入贝叶斯，fit进vec.transform(words)输入特征和标签y_train
# from sklearn.naive_bayes import MultinomialNB
# classifier = MultinomialNB()
# classifier.fit(vectorizer.transform(words), y_train)

# 模型评估模块
from sklearn.metrics import classification_report
# 测试集同样操作来一遍
test_words = []
for line_index in range(len(x_test)):
    try:
        #x_train[line_index][word_index] = str(x_train[line_index][word_index])
        test_words.append(' '.join(x_test[line_index]))
    except:
         print (line_index)
# print(test_words[0])
print(classifier.score(vec.transform(test_words), y_test))
# print(vec.transform(words))
predict=classifier.predict(vec.transform(test_words))
print(predict)

