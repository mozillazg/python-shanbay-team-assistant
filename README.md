shanbay team assistant
======================

[扇贝网](http://www.shanbay.com) 小组管理助手。

目前专为 [彪悍的人生无需解释](http://www.shanbay.com/team/detail/3352/) 小组定制。

如要用于其他小组，修改 settings.ini.example 和模板文件即可。


功能
----

* 更新小组成员加入条件
* 获取所有小组成员的打卡等情况
* 通过规则判断是否需要执行踢人等操作
* 发邮件
* 发帖
* 支持半自动/全自动执行查卡操作


使用
---

* 安装依赖: ```pip install -r requirements.txt```
* 执行

  ```
  cp settings.ini.example settings.ini
  # modify settings.ini
  python assistant.py
  python assistant.py -s settings.ini
  python assistant.py -h
  ```

