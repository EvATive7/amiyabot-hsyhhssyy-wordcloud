# 兔兔词云

让兔兔可以收集群友的消息并生成词云

**从1.5版本升级上来的用户，请阅读数据迁移章节了解将要发生什么事**

## 如何使用

- 兔兔在插件安装后，就会自动开始记录群友的聊天文本
- 查询词云例子如下图所示：

![兔兔查询词云例子](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/master/example_image/word_cloud_example.jpg)
![兔兔查询群词云例子](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/master/example_image/word_cloud_channel_example.jpg)
![兔兔分析词频例子](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/master/example_image/word_cloud_analyse_personal.jpg)
![兔兔分析群词频例子](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/master/example_image/word_cloud_analyse.jpg)

## 插件配置

前往控制台 >> 插件管理 >> 插件配置，管理本插件设置

## 数据迁移

**从1.5版本升级上来的用户，请阅读数据本章节了解发生了什么事**

在以前，用户的词云数据是存储在磁盘上的resource目录下（resource/word_cloud.db），不方便管理。
从2.0版本开始，该存储位置改为使用兔兔当前使用的数据库。因此在版本第一次加载的时候，兔兔会读取旧数据库里的数据，在兔兔当前的数据库中建立一张新表写入进去。这个过程可能会耗时很久，取决于你的数据库大小（平均速度约为每10秒5MB）。
如果你可以接受放弃旧数据，可以直接重命名旧的词云数据文件，插件将直接启动。
迁移完成后，旧数据库将会被重命名为word_cloud.db.bak，在确认本插件稳定运行无误后，您可以删除此文件。

## 安装依赖

注意，为了让该插件可以正常工作，需要安装依赖 `wordcloud==1.8.2.2`，插件内并不自带该依赖（因为太大了）

**wordcloud最近更新了1.9的新版本，和本插件不兼容，请使用1.8.2.2版本**

- 代码部署下部署：

    - 请在命令行执行 `pip install wordcloud==1.8.2.2`
    - 完成后请重启amiyabot

- 可执行文件部署：

    - 注意，使用此方法安装依赖，需要您对windows系统的cmd命令行操作有一定了解，插件仅对该方式提供有限的支持。
    - 想要在可执行文件部署的情况下使用该插件，需要您安装python。
    - 在cmd命令行执行 `pip install wordcloud==1.8.2.2` 安装依赖文件，如果只是出现了警告，可以暂时忽略。
    - 找到site-package目录的路径，方法如下：
        - 在cmd命令行下执行 `python -c 'import site; print(site.getsitepackages())'`
        - 系统会返回多个路径，在返回的路径中找到以site-packages结尾的那个路径，比如 `C:\\Python38\\lib\\site-packages`。复制这个路径（不包含引号）
    - 在amiyabot的resource文件夹下，用记事本打开文件python_support.yaml，如果该文件不存在就新建一个。
    - 找到并编辑sitePackagePath以开头的行，改为： `sitePackagePath: '[刚刚复制的路径]'`，如果不存在则新增此行。
        - 注意，上面的冒号后面有一个空格，且路径由单引号包围
        - 修改这个路径，将两个双斜杠 `\\` 替换为一个单斜杠 `\`
    - 比如按照上面那个例子路径修改的话，文件的内容就是
        ```
        sitePackagePath: 'C:\Python38\lib\site-packages'
        ```

        ![yaml文件内容](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/master/example_image/yaml_file_example.jpg)

    - 确认无误后请重启amiyabot，并查看启动时是否还有错误提示。
    - （话说你都安装了python了，不试试用代码部署amiyabot吗，这样本插件或者其他需要额外依赖的插件都好弄多了。）

- 如果不安装该依赖，兔兔只会收集群友的聊天文本，而无法生成词云图片。

## 其他注意事项

- 个人词云统计默认指一个用户同时在多个启用了本bot的群中展示的词云为多个群内聊天内容的合并统计，在配置中可修改。

## 备注

> [项目地址:Github](https://github.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/)

> [遇到问题可以在这里反馈(Github)](https://github.com/hsyhhssyy/amiyabot-hsyhhssyy-wordcloud/issues/new/)

> [如果上面的连接无法打开可以在这里反馈(Gitee)](https://gitee.com/hsyhhssyy/amiyabot-plugin-bug-report/issues/new)

> [Logo作者:Sesern老师](https://space.bilibili.com/305550122)

|  版本   | 变更  |
|  ----  | ----  |
| 1.0  | 初版登录商店 |
| 1.1  | 适配新版插件商店 |
| 1.2  | 修复在默认字符集不是Utf-8的机器上加载会出错的问题 |
| 1.3  | 将底色改为白色更清晰一些 |
| 1.4  | 新增可执行文件部署的相关指引 |
| 1.5  | 将几个兔兔常用指令加入词云屏蔽词 |
| 2.0  | 加入群词云统计支持，个人词云合并统计开关，支持词频分析，(感谢@)，数据库迁移 |
