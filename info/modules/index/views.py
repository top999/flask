from flask import render_template, session, request, jsonify

from info.models import User
from info.utils.response_code import RET
from . import index_blu


# 测试

@index_blu.route('/')
def index():
    # 获取到当前登录用户的id
    user_id= session.get('user_id')
    print(user_id)
    user =None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            return jsonify(erron=RET.DBERR)
    # 返回给前端查询结果
    data = {
        'user':user
    }
    return render_template('new/index.html',data=data)