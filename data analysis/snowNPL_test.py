from snownlp import SnowNLP
import pandas as pd


def get_score(text):             #
    s = SnowNLP(text)           # snownlp中的SnowNLP函数对text文本进行分词处理
    return s.sentiments         # sentiments函数进行情感分析，即获得文本的情感评分


df = pd.read_excel("LiHongLiang.xlsx")     # 把xlsx中的评论读入变量df中
df["score"] = df.comments.apply(get_score)    # 对comments列的所有文本分别进行分词和情感分析，并将情感分析结果导入score列
df.to_excel("LiHongLiang.xlsx")             # 把df的内容读出到xlsx文档
print(df.head())                            # 输出头部五行数据
