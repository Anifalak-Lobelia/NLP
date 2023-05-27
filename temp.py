import pandas as pd

# 读取csv文件
df = pd.read_csv('E:\\NLP\\data\\zhihu_result.csv')

# 创建id属性
df['id'] = range(1, len(df) + 1)

# 创建一个映射，将不同的question_title映射到一个唯一的id上
question_title_to_id = {title: idx for idx, title in enumerate(df['question_title'].unique(), start=1)}

# 创建question_id属性
df['question_id'] = df['question_title'].apply(lambda x: question_title_to_id[x])

# 将处理过的DataFrame写回csv
df.to_csv('E:\\NLP\\data\\zhihu_result.csv', index=False)
