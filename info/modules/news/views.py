from flask import render_template, g, request, jsonify, current_app
from info import db
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment, CommentLike
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    user = g.user
    news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    news = News.query.get(news_id)
    # 判断是否收藏该新闻，默认值为 false
    is_collected = False
    is_followed = False
    comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    comments = []
    # print(comment_list)
    # 判断用户是否收藏过该新闻
    if user:
        if news in user.collection_news:
            is_collected = True
        if news.user in user.followed:
            is_followed = True
        user_comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
        user_comment_ids = [comment_like.comment_id for comment_like in user_comment_likes]
        for comment in comment_list if comment_list else []:
            comment_dict = comment.to_dict()
            comment_dict['is_like'] = False
            if comment.id in user_comment_ids:
                comment_dict['is_like'] = True
            comment.append(comment_dict)
    data = {
        'news_dict': news_click_list,
        'user': user.to_dict() if user else None,
        'news': news.to_dict() if news else None,
        'is_collected': is_collected,
        'comments': comments,
        'is_followed': is_followed,
    }
    # 返回数据
    return render_template('news/detail.html', data=data)


@news_blu.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏"""
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 获取参数
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 判断参数
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # action在不在指定的两个值：'collect','cancel_collect'内
    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    # 查询新闻,并判断新闻是否存在
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        # 返回
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def add_news_comment():
    """添加评论"""

    # 用户是否登陆
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")
    # 判断参数是否正确
    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 查询新闻是否存在并校验
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")
    # 初始化评论模型，保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id
    # 配置文件设置了自动提交,自动提交要在return返回结果以后才执行commit命令,如果有回复
    # 评论,先拿到回复评论id,在手动commit,否则无法获取回复评论内容
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    print(1111)
    """
    评论点赞
    :return:
    """
    # 用户是否登陆
    global comment_like
    user = g.user
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg="用户未登录")
    # 取到请求参数
    comment_id = request.json.get('comment_id')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 判断参数
    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.DBERR, errmsg='查询参数失败')
    if action not in ('add', 'remove'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 获取到要被点赞的评论模型
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询参数数据')
    # action的状态,如果点赞,则查询后将用户id和评论id添加到数据库
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论数据不存在')
    if action == 'add':
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
    # 点赞评论
    # 更新点赞次数
    if not comment_like:
        comment_like = CommentLike()
        comment_like.comment_id = comment_id
        comment_like.user_id = user.id
        db.session.add(comment_like)
        comment.like_count += 1

    # 取消点赞评论,查询数据库,如果以点在,则删除点赞信息
    else:
        comment_like = CommentLike.query.filter_by(user_id=user.id, comment_id=comment_id).first()
        if comment_like:
            db.session.delete(comment_like)
            comment.like_count -= 1
    # 更新点赞次数
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='操作失败')

    # 返回结果
    return jsonify(errno=RET.OK, errmsmg='操作成功')
