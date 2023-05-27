# 21122924 刘育杰 智能科学与技术
from django.views.decorators.csrf import csrf_exempt
import time
from django.shortcuts import render,HttpResponse,redirect
import pandas as pd
from datetime import datetime
from app01.templatetags.recommand import recommend_question
import jieba
import jieba.analyse
from wordcloud import WordCloud
import numpy as np
from PIL import Image
# 函数 Create your views here.

@csrf_exempt
def login(request):
    if request.method == "GET":
        return render(request,"login.html")
    else:
        username = request.POST.get("user")
        password = request.POST.get("pwd")
        if username == "root" and password == "12345":
            time.sleep(1.5)
            return redirect('/home/?date=2023-05-10')
        else:
            return render(request,"login.html")




from django.http import HttpResponseBadRequest


def topic(request):
    # 获取查询参数question_id或question_title
    question_id = request.GET.get('question_id', None)
    question_title = request.GET.get('question_title', None)
    # 如果question_id和question_title都为空，则返回错误
    if not question_id and not question_title:
        return HttpResponseBadRequest("Invalid question_id or question_title")

    # 如果没有传递question_id，则通过question_title查找对应的question_id
    if not question_id and question_title:
        # 读取CSV文件，找到对应question_title的数据
        df = pd.read_csv('E:/NLP/Project/zhihu_result.csv', encoding='utf-8')
        for i, row in df.iterrows():
            if str(row['question_title']) == question_title:
                question_id = str(row['question_id'])
                # 重定向到带有question_id的URL
                return redirect('/topic/?question_id=' + question_id)

    # 读取CSV文件，找到对应question_id或question_title的数据
    content_list = []
    df = pd.read_csv('E:/NLP/Project/zhihu_result.csv', encoding='utf-8')
    # 如果question_id存在，以question_id为依据搜索
    if question_id:
        for i, row in df.iterrows():
            if str(row['question_id']) == question_id:
                content_list.append({'id': row['id'], 'content': str(row['content'])})
                if question_title is None:
                    question_title = row['question_title']
    # 如果question_title存在，以question_title为依据搜索
    elif question_title:
        for i, row in df.iterrows():
            if str(row['question_title']) == question_title:
                content_list.append({'id': row['id'], 'content': str(row['content'])})
                question_id = row['question_id']
    if question_title is None or question_id is None:
        return HttpResponseBadRequest("Question not found")
    # 获取相似的问题
    similar_questions = recommend_question(question_title)
    # 去除相似问题中的重复问题
    similar_questions = list(set(similar_questions))
    # 读取CSV文件，找到对应question_id或question_title的数据
    content_list = []
    content_text = ''
    question_title = None
    df = pd.read_csv('E:/NLP/Project/zhihu_result.csv', encoding='utf-8')
    for i, row in df.iterrows():
        if str(row['question_id']) == question_id:
            content_list.append({'id': row['id'], 'content': str(row['content'])})
            content_text += str(row['content']) + ' '
            if question_title is None:
                question_title = row['question_title']
    # 生成关键词
    keyword_list = jieba.analyse.extract_tags(content_text, topK=100, withWeight=True)
    keywords = {item[0]: item[1] for item in keyword_list}
    # 生成词云图
    # 读取自定义形状图片并转换为数组
    custom_shape_path = 'E:/NLP/Project/app01/static/image/example.jpg'
    custom_shape = np.array(Image.open(custom_shape_path).convert('L'))
    wordcloud = WordCloud(font_path='simhei.ttf', background_color="white", max_words=100, mask=custom_shape)
    wordcloud.generate_from_frequencies(keywords)
    wordcloud_image_path = 'E:/NLP/Project/app01/static/image/wordcloud.png'
    wordcloud.to_file(wordcloud_image_path)
    # 将数据传递给模板
    return render(request, 'topic.html', {'content_list': content_list, 'question_title': question_title,
                                          'similar_questions': similar_questions,
                                          'wordcloud_img_url': 'E:/NLP/Project/app01/static/image/wordcloud.png'})


def content_detail(request):
    # 获取查询参数id
    content_id = request.GET.get('id', None)
    # 读取CSV文件，找到对应id的数据
    df = pd.read_csv('E:/NLP/Project/zhihu_result.csv', encoding='utf-8')
    for i, row in df.iterrows():
        if str(row['id']) == content_id:
            created_time = datetime.fromisoformat(row['created_time'].replace("Z", "+00:00"))
            formatted_time = created_time.strftime("%Y-%m-%d, %H:%M:%S")
            # 预处理hot值
            hot = row['hot']
            if hot > 1:
                hot = 1
            content_data = {
                'id': row['id'],
                'content': str(row['content']),
                'question_title': row['question_title'],
                'author_name': row['author_name'],
                'created_time': formatted_time,
                'comment_count': row['comment_count'],
                'fans_count': row['fans_count'],
                'voteup_count': row['voteup_count'],
                'emotion_label': row['emotion_label'],
                'emotion_score': row['emotion_score'],
                'key_words': row['key_words'],
                'key_sentence': row['key_sentence'],
                'fake': row['fake'],
                'hot': hot,  # 添加hot值到context中
            }
            break
    # 将数据传递给模板
    return render(request, 'content_detail.html', content_data)

def temp(request):
    return render(request, 'temp.html')

from django.shortcuts import render
from .templatetags.search.sim_search import search_similar_questions
from django.http import JsonResponse

def get_question_url(question_id):
    base_url = "http://127.0.0.1:8000/topic/?question_id="
    return base_url + str(question_id)

def home(request):
    # 获取查询参数date
    date_str = request.GET.get('date', None)
    # 如果没有提供date参数，或者date参数格式错误，选择重定向到其他页面
    if date_str is None:
        return redirect('/home')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return HttpResponse('Invalid date format')

    # 读取CSV文件，找到对应日期的数据
    data_list = []
    df = pd.read_csv('E:/NLP/Project/zhihu_result.csv', encoding='utf-8')
    for i, row in df.iterrows():
        if i % 20 == 0 and str(row[16]) == date_str:
            data_list.append({'id': str(row[18]), 'question_title': str(row[0])})
    # 统计 'class' 列的频数
    class_data = [{'name': '时政', 'value': 565}, {'name': '娱乐', 'value': 1815}, {'name': '科技', 'value': 880}, {'name': '游戏', 'value': 220}, {'name': '财经', 'value': 45}, {'name': '家居', 'value': 425}, {'name': '社会', 'value': 365}, {'name': '股票', 'value': 280}, {'name': '教育', 'value': 380}, {'name': '房产', 'value': 60}, {'name': '时尚', 'value': 120}]
    # 将数据传递给模板
    return render(request, 'home.html', {'data_list': data_list, 'class_data': class_data})

from django.http import JsonResponse

@csrf_exempt
def search(request):
    search_text = request.POST.get('search_text', '')
    results = search_similar_questions(search_text)

    results = [{'question_title': result['question_title'], 'score': result['score'],
                'url': get_question_url(result['question_id'])} for result in results]
    print(results)
    return render(request, 'search.html', {'results': results})


