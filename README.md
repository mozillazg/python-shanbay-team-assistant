# shanbay team assistant

[扇贝网](http://www.shanbay.com) 小组管理助手。

目前专为 [彪悍的人生无需解释](http://www.shanbay.com/team/detail/3352/) 小组定制。

如要用于其他小组，修改 settings.ini.example 和模板文件即可。


## 功能

* 更新小组成员加入条件
* 获取所有小组成员的打卡等情况
* 通过规则判断是否需要执行踢人等操作
* 发站内短信
* 发帖
* 回帖
* 发送欢迎、恭喜、警告、踢人站内短信
* 支持半自动/全自动执行查卡操作
* 支持发送通知短信（给所有组员群发短信）


## 使用

### 安装依赖
```pip install -r requirements.txt```

### 修改配置文件
复制 settings.ini.example 为 settings.ini，修改其中的配置项。

### 修改模板文件
复制 templates 目录下的 .example 文件为 .txt 文件，并修改 txt 文件的内容。

### 查卡
命令行下执行 ```python assistant.py```

可以通过 -s 指定配置文件： ``` python assistant.py -s settings_biaohan.ini```

### 发送通知短信
命令行下执行 ```python assistant.py  -a announce.txt -t "来自小组的邀请"```

其中 ```announce.txt``` 是通知内容,位于 templates 目录，可以参考目录下的 ```templates/announce.txt.example```， ```来自小组的邀请``` 是通知的标题。

