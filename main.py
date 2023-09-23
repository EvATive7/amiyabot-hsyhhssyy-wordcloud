import asyncio
import sqlite3
import os
import re
import sys

from amiyabot import AmiyaBot, Message, Chain, log
from core.util import read_yaml
from core import AmiyaBotPluginInstance
from collections import defaultdict

curr_dir = os.path.dirname(__file__)
db_file = f'{curr_dir}/../../resource/word_cloud.db'

enabled = False

try:
    try:
        python_support = read_yaml(f'{curr_dir}/../../resource/python_support.yaml')
        sys.path.append(python_support.sitePackagePath)
    except:
        pass
    from wordcloud import WordCloud
    enabled = True
except ModuleNotFoundError:
    log.info('无法加载wordcloud依赖，如果您是代码部署，请执行pip install wordcloud，如果您是可执行文件部署，请根据插件说明中的内容执行对应操作。')
    enabled = False

#初始化停用词
stop_words = []
file_object2 = open(f"{curr_dir}/resource/word_cloud_stop_words_cn.txt",'r', encoding='utf-8')
try:
    lines = file_object2.readlines()
    for line in lines:
        stop_words.append(line.strip())
finally:
    file_object2.close()

file_object2 = open(f"{curr_dir}/resource/word_cloud_stop_words_custom.txt",'r', encoding='utf-8')
try:
    lines = file_object2.readlines()
    for line in lines:
        stop_words.append(line.strip())
finally:
    file_object2.close()

log.info(f'WordCloud stop words loaded total {len(stop_words)} words')

def get_db_connection_whether_exists():
    if os.path.exists(db_file):
        return sqlite3.connect(db_file)
        
    else:        
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE WORD_CLOUD
            (WORD           TEXT    NOT NULL,
            USER_ID         INT     NOT NULL,
            QUANTITY        INT     NOT NULL,
            CHANNEL_ID      INT     NOT NULL);''')
        conn.commit()
        return conn

async def any_talk(data: Message):
    
    # log.info('AnyTalk Collect Word Cloud')

    #收集好分词后的群友句子
    words = data.text_words

    #以Sqlite的形式存到fileStorage下面
    conn = get_db_connection_whether_exists()
    
    user_id = data.user_id
    channel_id = data.channel_id

    c = conn.cursor()
    for word in words:
        # 获取当前Quantity
        c.execute("select QUANTITY from WORD_CLOUD where USER_ID = ? and WORD = ? and CHANNEL_ID = ?",(user_id,word,channel_id))
        if len(c.fetchall()) <=0 :
            c.execute('INSERT INTO WORD_CLOUD (USER_ID,WORD,QUANTITY,CHANNEL_ID) values (?,?,1,?)' ,(user_id,word,channel_id))
        else:
            c.execute('UPDATE WORD_CLOUD SET QUANTITY = QUANTITY +1 where USER_ID = ? and WORD = ? and CHANNEL_ID = ?' ,(user_id,word,channel_id))

    conn.commit()

    return False,0

class WordCloudPluginInstance(AmiyaBotPluginInstance):
    def install(self):
        if not os.path.exists(f'{curr_dir}/../../resource/word_cloud'):
            os.makedirs(f'{curr_dir}/../../resource/word_cloud')

        # 1.5无感升级至1.6:
        # 检查数据库是否存在名为CHANNEL_ID的列，如果没有就添加。
        conn = get_db_connection_whether_exists()
        c = conn.cursor()
        c.execute("PRAGMA table_info('WORD_CLOUD')") 
        columns = c.fetchall()
        column_names = [column[1] for column in columns]
        if not 'CHANNEL_ID' in column_names:
            c = conn.cursor()
            c.execute('''ALTER TABLE WORD_CLOUD 
                         ADD COLUMN CHANNEL_ID INT NOT NULL DEFAULT 0;''')
            log.info(f'WordCloud DB updated to 1.6 version')

bot = WordCloudPluginInstance(
    name='词云统计',
    version='1.8',
    plugin_id='amiyabot-hsyhhssyy-wordcloud',
    plugin_type='',
    description='让兔兔可以统计群用户的词云。1.4版开始对可执行文件部署用户提供支持。',
    document=f'{curr_dir}/README.md',
    instruction=f'{curr_dir}/README_USE.md',
    global_config_schema=f'{curr_dir}/config_schema.json',
    global_config_default=f'{curr_dir}/config_default.yaml'
)

@bot.on_message(verify=any_talk, check_prefix=False)
async def _(data: Message):
    return

def check_wordcloud_availability(data):
    if not os.path.exists(db_file) :
        return Chain(data).text('兔兔的词云功能没有开放哦。')
    
    if not enabled :
        return Chain(data).text('兔兔目前还不会绘制词云图片，请管理员安装对应依赖。')
    
    return None

@bot.on_message(keywords=['查看词云','查询词云'], level = 5)
async def check_wordcloud(data: Message):

    # log.info('Create Word Cloud')

    merge = bool(bot.get_config('personalMerge'))

    ava = check_wordcloud_availability(data)
    if ava is not None : return ava

    user_id = data.user_id

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    channelSQL = ' '
    if not merge:
        channelSQL = f" and CHANNEL_ID = '{data.channel_id}'"
    c.execute(f"select QUANTITY,WORD from WORD_CLOUD where USER_ID = '{user_id}'{channelSQL}")

    frequencies = {}
    for row in c:
        if f'{row[1]}' not in stop_words:
            if f'{row[1]}' not in frequencies.keys():
                frequencies[row[1]]=row[0]
            else:
                frequencies[row[1]]+=row[0]

    if len(frequencies) <=0 :
        return Chain(data).text('兔兔还没有收集到词频噢，请让我多听一会儿。')

    # wordcloud = WordCloud(font_path =  "fileStorage/GenJyuuGothic-Normal-2.ttf").generate_from_frequencies(frequencies)    
    wordcloud = WordCloud(font_path =  f'{curr_dir}/resource/msyh.ttf',background_color='white').generate_from_frequencies(frequencies)
    wordcloud.to_file(f'{curr_dir}/../../resource/word_cloud/word_cloud_{data.user_id}.jpg')

    channelText = ''
    if not merge:
        channelText = '在本群的词频'
    return Chain(data).text(f'兔兔为你{channelText}生成了一张词云图：').image(f'{curr_dir}/../../resource/word_cloud/word_cloud_{data.user_id}.jpg')

@bot.on_message(keywords=['查看群词云','查询群词云'], level = 5)
async def check_channel_wordcloud(data: Message):
    ava = check_wordcloud_availability(data)
    if ava is not None : return ava

    channel_id = data.channel_id

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"select QUANTITY,WORD,USER_ID from WORD_CLOUD where CHANNEL_ID = '{channel_id}'")

    frequencies = {}
    for row in c:
        if f'{row[1]}' not in stop_words:
            if f'{row[1]}' not in frequencies.keys():
                frequencies[row[1]]=row[0]
            else:
                frequencies[row[1]]+=row[0]

    if len(frequencies) <=0 :
        return Chain(data).text('兔兔还没有收集到词频噢，请让我多听一会儿。')

    # wordcloud = WordCloud(font_path =  "fileStorage/GenJyuuGothic-Normal-2.ttf").generate_from_frequencies(frequencies)    
    wordcloud = WordCloud(font_path =  f'{curr_dir}/resource/msyh.ttf',background_color='white').generate_from_frequencies(frequencies)
    wordcloud.to_file(f'{curr_dir}/../../resource/word_cloud/word_cloud_channel_{data.channel_id}.jpg')

    return Chain(data).text('兔兔为本群生成了一张词云图：').image(f'{curr_dir}/../../resource/word_cloud/word_cloud_channel_{data.channel_id}.jpg')


@bot.on_message(keywords=['分析群词频'],level=5)
async def get_word_rank(data:Message):

    ava = check_wordcloud_availability(data)
    if ava is not None : return ava

    channel = data.channel_id
    c = get_db_connection_whether_exists().cursor()
    c.execute(f"select QUANTITY,WORD,USER_ID from WORD_CLOUD where CHANNEL_ID = '{channel}'")

    result = list(c)

    if len(result) <=0 :
        return Chain(data).text('兔兔还没有收集到词频噢，请让我多听一会儿。')
    
    result = [item for item in result if item[1] not in stop_words] #过滤词汇

    # 一、找出总提及次数排名前三的词汇
    word_counts = defaultdict(int)
    for count, word, _ in result:
        word_counts[word] += count

    # 根据词汇的提及次数进行降序排序
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    #print("一、总提及次数排名前三的词汇：")
    top_words = []
    select_len = min(3,len(sorted_words))
    
    for i, (word, count) in enumerate(sorted_words[:select_len], start=1):
        top_words.append(
            {
                'word':word,
                'count':count,
                'person_id':0000,
                'person_count':0
            }
        )

    # 二、找出对应词汇提及最多的人ID
    for word in top_words:
        rank_person = [item for item in result if item[1] == word['word']]
        rank_person = sorted(rank_person, key=lambda x: x[0], reverse=True)
        word['person_id'] = rank_person[0][2]
        word['person_count'] = rank_person[0][0]

    res = Chain(data=data, at=False)
    res.text('兔兔发现！').text('\n')
    index = 0
    for word in top_words:
        word_text = word['word']
        word_count = word['count']
        word_person_id = word['person_id']
        word_person_count = word['person_count']

        if (index == 0):
            order_word = '最'
        elif (index == 1):
            order_word = '第二'
        elif (index == 2):
            order_word = '第三'

        res.text(f'本群内被提及{order_word}多的词汇是“{word_text}”（{word_count}次），其中提及最多次的人是')
        res.at(word_person_id)
        res.text(f'，ta提及了{word_person_count}次；').text('\n')

        index += 1

    return res


@bot.on_message(keywords=['分析词频'],level=5)
async def get_personal_word_rank(data:Message):

    merge = bool(bot.get_config('personalMerge'))

    ava = check_wordcloud_availability(data)
    if ava is not None : return ava

    user_id = data.user_id

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    channelSQL = ' '
    if not merge:
        channelSQL = f" and CHANNEL_ID = '{data.channel_id}'"
    c.execute(f"select QUANTITY,WORD from WORD_CLOUD where USER_ID = '{user_id}'{channelSQL}")

    frequencies = {}
    for row in c:
        if f'{row[1]}' not in stop_words:
            if f'{row[1]}' not in frequencies.keys():
                frequencies[row[1]]=row[0]
            else:
                frequencies[row[1]]+=row[0]

    frequencies = sorted(frequencies.items(),key=lambda x: x[1],reverse=True)

    if len(frequencies) <=0 :
        return Chain(data).text('兔兔还没有收集到词频噢，请让我多听一会儿。')

    max_analyse = min(3,len(frequencies))

    res = Chain(data).text('兔兔发现')

    index = 0
    for word in frequencies:
        text = word[0]
        quantity = word[1]

        if (index == 0):
            order_word = '最'
        elif (index == 1):
            order_word = '第二'
        elif (index == 2):
            order_word = '第三'

        res.text(f'你{order_word}喜欢用的词汇是“{text}”，你一共使用了{quantity}次；').text('\n')

        index += 1
        if (index >= max_analyse):
            break

    return res
