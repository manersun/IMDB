#coding=utf-8
import pandas as pd
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV


def review_to_text(review, remove_stopwords):
    raw_text = BeautifulSoup(review, 'lxml').get_text() #去掉html标记
    letters = re.sub('[^a-zA-Z]','',raw_text) #去掉非字母字符
    words = letters.lower().split()
    if remove_stopwords:  #remove_stopwords 是boolean类型，是否去掉停用词   需要下载停用词列表。
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words]
    return words #返回每条评论经过三项处理的词汇列表

train = pd.read_csv('../data/labeledTrainData1.tsv', delimiter='\t')
test = pd.read_csv('../data/testData1.tsv', delimiter='\t')
# print train.head()
# print test.head()
X_train=[]
for review in train['review']:
    X_train.append(''.join(review_to_text(review, True)))
X_test=[]
for review in test['review']:
    X_test.append(''.join(review_to_text(review, True)))
y_train = train['sentiment']
pip_count = Pipeline([('count_vec', CountVectorizer(analyzer='word')), ('mnb', MultinomialNB())])#analyzer : string, {‘word’, ‘char’, ‘char_wb’} or callable，特征由什么组成
pip_tfidf = Pipeline([('tfidf_vec', TfidfVectorizer(analyzer='word')), ('mnb', MultinomialNB())])
#binary为True  所有非0都表示成1，ngram_range表示n的范围，alpha表示平滑值
params_count = {'count_vec_binary':[True, False], 'count_vec_ngram_range':[(1, 1), (1, 2)], 'mnb_alpha':[0.1, 1.0, 10.0]} #参数意思查看sklearn官网
params_tfidf = {'tfidf_vec_binary':[True, False], 'tifid_vec_ngram_range':[(1, 1), (1, 2)], 'mnb_alpha':[0.1, 1.0, 10.0]}
#用与超参数组合的网格搜索，寻找最佳的一组参数组合，cv=4即4折交叉验证。 n_jobs并行运行的作业数 -1表示使用全部的处理器  verbose控制冗长，值越大信息越多
gs_count = GridSearchCV(pip_count, params_count, cv=4, n_jobs=-1, verbose=1)
gs_count.fit(X_train, y_train)
print gs_count.best_score_
print gs_count.best_params_
count_y_predict= gs_count.predict(X_test)
gs_tfidf = GridSearchCV(pip_tfidf, params_tfidf, cv=4, n_jobs=-1, verbose=1)
gs_tfidf.fit(X_train, y_train)
tfidf_y_predict = gs_tfidf.predict(X_test)

submission_count = pd.DataFrame({'id':test['id'],'sentiment':count_y_predict})
submission_tfidf = pd.DataFrame({'id':test['id'],'sentiment':tfidf_y_predict})


####CountVectorizer 实例，，，词频统计       TfidfVectorizer继承了CountVectorizer 只是加了TF_IDF的一些计算，词频和逆向文件频率
# texts=["dog cat fish","dog cat cat","fish bird", 'bird']
# cv = CountVectorizer()
# cv_fit=cv.fit_transform(texts)
#
# print(cv.get_feature_names())
# print(cv_fit.toarray())
# #['bird', 'cat', 'dog', 'fish']
# #[[0 1 1 1]
# # [0 2 1 0]
# # [1 0 0 1]
# # [1 0 0 0]]
#
# print(cv_fit.toarray().sum(axis=0))
# #[2 3 2 2]