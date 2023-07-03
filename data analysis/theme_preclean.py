from snownlp import SnowNLP
import pandas as pd
import re


def clean(content):       #
    content_S = []
    emoji_pattern = re.compile((u'[\U00010000-\U0010ffff\\uD800-\\uDBFF\\uDC00-\\uDFFF\\u2716]'))
    aaa = re.compile((u'[\u0000-\uffff]'))
    for line in content:
        line = emoji_pattern.sub('', line)
        line = line.replace("\xa1", "")
        line = line.replace("\ufe0f", "")
        line = line.replace("\u22ef", "")
        line = line.replace("\u200d", "")
        line = line.replace("\u2727", "")
        line = line.replace("\u270c", "")
        line = line.replace("\u0e51", "")
        line = line.replace("\u0e05", "")
        line = line.replace("\u0300", "")
        line = line.replace("\u2022", "")
        line = line.replace("\u3141", "")
        line = line.replace("\u0301", "")
        line = line.replace("\ue627", "")
        # line = aaa.sub('', line)
        content_S.append(line)
    return content_S         # sentiments函数进行情感分析，即获得文本的情感评分


df = pd.read_csv("themeSpider_comments.csv").astype(str)     # 把xlsx中的评论读入变量df中
content = df.content.values.tolist()        # 将评论和发评人转换为list格式
actor = df.actor.values.tolist()


content_S = clean(content)
df_content = pd.DataFrame({'actor': actor, 'content': content_S})

df_content.to_csv("themeSpider_comments1.csv", encoding='gbk')             # 把df的内容读出到xlsx文档
print(df.head())                            # 输出头部五行数据
