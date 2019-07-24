from flask import render_template

from . import index_blu


# 测试
@index_blu.route('/')
def index():
    # 获取到当前登录用户的id
    # 返回给前端查询结果
    return render_template('new/index.html',data={})