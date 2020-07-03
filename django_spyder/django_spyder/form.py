# /usr/bin/python
# -*- coding=utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render

# 表单

from django.views.decorators.csrf import csrf_protect
import pymysql
import time
from . import spyder

@csrf_protect
def form_view(request):
    return render(request, 'form.html')

def form_submit(request):
    # 从前端接收到数据 开始爬虫 存入数据
    print('hahahahha')
    request.encording='utf-8'
    user_id = request.POST['user_id']
    screen_name = request.POST['screen_name']
    cookie = request.POST['cookie']
    print(user_id)
    print(screen_name)
    print(cookie)
    if 'user_id' in request.POST:
        message = {'user_id':user_id,'screen_name':screen_name,'cookie':cookie}
    else:
        message = '接收不到数据'
    spyder.main(user_id,screen_name,cookie)

    return HttpResponse(user_id)




def test(request):
    uid = request.GET.get('uid')
    conn = pymysql.connect(host='localhost', user='root', passwd='root', db='db_weibo', charset="utf8")
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from tb_user where id={};".format(uid))
    user_info = cursor.fetchall()
    cursor.execute(
            """
            select t2.*,t3.user_id as rp_user_id,t3.retweet_id as rp_retweet_id,t3.text as rp_text,t3.pics as rp_pics,t3.screen_name as rp_screen_name from
    (select * from tb_weibo as t1 where t1.user_id = {}) as t2
    left join tb_weibo as t3
    on t2.retweet_id = t3.id
    order by t2.created_at desc
    limit 10;
            """.format(uid)
        )
    weibo_info = cursor.fetchall()
    for weibo in weibo_info:
        weibo['pics'] = weibo['pics'].split(',') if weibo['pics'] else []
        weibo['rp_pics'] = weibo['rp_pics'].split(',') if weibo['rp_pics'] else []
    return render(request, 'show.html', {'user_info': user_info[0], 'weibo_info': weibo_info})

