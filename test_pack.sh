#!/bin/sh

zip -q -r amiyabot-hsyhhssyy-wordcloud-1.4.zip *
rm -rf ../../amiya-bot-v6/plugins/amiyabot-hsyhhssyy-wordcloud-*
mv amiyabot-hsyhhssyy-wordcloud-*.zip ../../amiya-bot-v6/plugins/
docker restart amiya-bot 