- 修改数据库配置

  1. settings.py

  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/settings.png)

  2. spyder.py

  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/spyder.png)

- 数据库建库、建表

  ```sql
  # 删除微博库
  DROP DATABASE IF EXISTS `db_weibo`;
  # 创建微博库
  CREATE DATABASE IF NOT EXISTS `db_weibo` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  USE `db_weibo`;
  
  DROP TABLE IF EXISTS `tb_user`;
  CREATE TABLE IF NOT EXISTS `tb_user` (
    `uuid` int unsigned NOT NULL AUTO_INCREMENT,
    `id` varchar(20) NOT NULL UNIQUE,
    `screen_name` varchar(50) DEFAULT '',
    `gender` tinyint unsigned DEFAULT 0,
    `statuses_count` int unsigned DEFAULT 0,
    `follow_count` int unsigned DEFAULT 0,
    `followers_count` int unsigned DEFAULT 0,
    `description` varchar(1000) DEFAULT '',
    `profile_image_url` varchar(500) DEFAULT '',
    `cover_image_phone` varchar(500) DEFAULT '',
    PRIMARY KEY (`uuid`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  # 创建微博数据表
  DROP TABLE IF EXISTS `tb_weibo`;
  CREATE TABLE IF NOT EXISTS `tb_weibo` (
    `uuid` int unsigned NOT NULL AUTO_INCREMENT,
    `id` varchar(20) NOT NULL UNIQUE,
    `bid` varchar(20) NOT NULL,
  	`user_id` varchar(20) NOT NULL,
  	`screen_name` varchar(50) DEFAULT '',
    `created_at` date DEFAULT '1000-01-01',
    `source` varchar(50) DEFAULT '',
    `text` text,
    `pics` varchar(1000) DEFAULT '',
    `media` varchar(500) DEFAULT '',
    `attitudes_count` int unsigned DEFAULT 0,
    `comments_count` int unsigned DEFAULT 0,
    `reposts_count` int unsigned DEFAULT 0,
    `retweet_id` varchar(20) DEFAULT '',
    PRIMARY KEY (`uuid`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  ```

- 启动

  ```
  python manager.py runserver
  ```

- 页面url 

  1. /
  2. /form_view

  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/main.png)


- 如何获取user_id和screen_name

  打开网址<https://weibo.cn>，搜索我们要找的人，如"人民日报"，进入她的主页；

  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/user_id.png)

- 如何获取cookie

  1.用Chrome打开<https://passport.weibo.cn/signin/login>；<br>
  2.输入微博的用户名、密码，登录，如图所示：
  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/cookie1.png)
  登录成功后会跳转到<https://m.weibo.cn>;<br>
  3.按F12键打开Chrome开发者工具，在地址栏输入并跳转到<https://weibo.cn>，跳转后会显示如下类似界面:
  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/cookie2.png)
  4.依此点击Chrome开发者工具中的Network->Name中的weibo.cn->Headers->Request Headers，"Cookie:"后的值即为我们要找的cookie值，复制即可，如图所示：
  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/cookie3.png)

- 获取到信息后填入，点击请求，点击查询可查询后台处理状态，如果处理完毕则跳转到生成的页面

  ![](https://raw.githubusercontent.com/WangJINGJING233/DJANGO_SPYDER/master/images/show.png)

  

  
