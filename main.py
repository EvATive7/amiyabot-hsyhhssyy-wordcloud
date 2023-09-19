import asyncio
import sqlite3
import os
import re
import sys

from amiyabot import AmiyaBot, Message, Chain, log , PluginInstance
from core.util import read_yaml

curr_dir = os.path.dirname(__file__)
db_file = f'{curr_dir}/../../resource/word_cloud.db'

def load_by_support():
    try:
        python_support = read_yaml(f'{curr_dir}/../../resource/python_support.yaml')
        sitePackagePath = python_support.sitePackagePath
        sys.path.append(sitePackagePath)
        from wordcloud import WordCloud
        enabled = True
    except:
        log.info('无法加载wordcloud依赖，如果您是代码部署，请执行pip install wordcloud，如果您是可执行文件部署，请根据插件说明中的内容执行对应操作。')
        enabled = False

enabled = False
try:
    from wordcloud import WordCloud
    enabled = True
except ModuleNotFoundError:
    load_by_support()

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

class WordCloudPluginInstance(PluginInstance):
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
    version='1.6',
    plugin_id='amiyabot-hsyhhssyy-wordcloud',
    plugin_type='',
    description='让兔兔可以统计群用户的词云。1.4版开始对可执行文件部署用户提供支持。',
    document=f'{curr_dir}/README.md'
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

    ava = check_wordcloud_availability(data)
    if ava is not None : return ava

    user_id = data.user_id

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"select QUANTITY,WORD from WORD_CLOUD where USER_ID = '{user_id}'")

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

    return Chain(data).text('兔兔为你生成了一张词云图：').image(f'{curr_dir}/../../resource/word_cloud/word_cloud_{data.user_id}.jpg')

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