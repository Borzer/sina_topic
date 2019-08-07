import csv, collections, jieba.analyse
from pyecharts import options
from pyecharts.globals import SymbolType
from pyecharts.charts import Pie, Bar, Map, WordCloud,Page


def csv_todict(index):
    with open('sina_topic.csv', 'r', encoding='utf-8') as f:
        csv_read = csv.reader(f)
        userinfo = [columns[index] for columns in csv_read]
        dic = collections.Counter(userinfo)
        # 删除空字符
        if '' in dic:
            dic.pop('')
        return dic


# 分析性别
def analysis_sex():
    # 读取性别列
    dic = csv_todict(2)

    # 生成二维数组
    sex_count_list = [list(i) for i in zip(dic.keys(), dic.values())]
    # 生成饼图
    pie = (
        Pie()
        .add('', sex_count_list)
        .set_colors(['red', 'blue'])
        .set_global_opts(title_opts=options.TitleOpts(title='周杰伦打榜性别分析'))
        .set_series_opts(label_opts=options.LabelOpts(formatter='{b}:{c}'))
    )
    return pie

# 分析年龄
def analysis_age():
    # 读取年龄列
    dic = csv_todict(3)

    # 按照年龄进行排序
    sorted_dic = {}
    for key in sorted(dic):
        sorted_dic[key] = dic[key]

    # 生成柱状图
    bar = (
        Bar()
        .add_xaxis(list(sorted_dic.keys()))
        .add_yaxis('周杰伦打榜粉丝数年龄分析',list(sorted_dic.values()))
        .set_global_opts(yaxis_opts=options.AxisOpts(name='数量'),
                         xaxis_opts=options.AxisOpts(name='年龄'))
    )
    return bar

# 地区分析
def analysis_area():
    dic = csv_todict(4)
    area_count_list = [list(z) for z in zip(dic.keys(),dic.values())]
    map = (
        Map()
        .add('周杰伦打榜粉丝地区分析',area_count_list,"china")
        .set_global_opts(visualmap_opts=options.VisualMapOpts(max_=200))
    )
    return map

# 微博内容关键词分析
def analysis_text():
    # 读取微博内容
    dic = csv_todict(6)
    # 数据清洗
    jieba.analyse.set_stop_words('stop_words.txt')
    # 词数统计
    words_count_list = jieba.analyse.textrank(''.join(dic.keys()),topK=50,withWeight=True)

    # 生成词云
    word_cloud = (
        WordCloud()
        .add('',words_count_list,word_size_range=[20,100],shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=options.TitleOpts(title='周杰伦打榜微博内容分析'))
    )
    return word_cloud


if __name__ == '__main__':
    page = Page()
    page.add(analysis_sex(), analysis_age(),analysis_area(),analysis_text())
    page.render('text.html')
