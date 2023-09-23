from datetime import datetime

from peewee import AutoField,CharField,IntegerField,TextField

from amiyabot.database import ModelClass

from core.database.plugin import db

class AmiyaBotWordCloudDataBase(ModelClass):
    id: int = AutoField()
    word = TextField()
    user_id = CharField()
    quantity = IntegerField()
    channel_id = CharField()

    class Meta:
        database = db
        table_name = "amiyabot-hsyhhssyy-wordcloud-data"