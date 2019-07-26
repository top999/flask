from flask import session, jsonify, current_app, render_template, request

from info.models import User, News, Category
from info.utils import constants
from info.utils.response_code import RET
from . import index_blu


# 测试

@index_blu.route('/')
def index():
    # 获取到当前登录用户的id
    user_id= session.get('user_id')
    # print(user_id)
    user =None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            return jsonify(erron=RET.DBERR)

    # 获取到当前登录用户的id
    user_id = session.get('user_id')
    user = None
    try:
        user = User.query.filter_by(id = user_id).first()
        # print(user_id)
    except Exception as e:
        current_app.logger.error(e)
    # 右侧新闻排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(10).all()
        # print(clicks_news)
    except Exception as e:
        current_app.logger.error(e)
    # 按照点击量排序查询出点击最高的前10条新闻
    clicks_news_li = []
    for new_abj in clicks_news:
        clicks_news_dict = new_abj.to_basic_dict()
        clicks_news_li.append(clicks_news_dict)
    # 获取新闻分类数据
    category_all = Category.query.all()
    # 定义列表保存分类数据
    categories = []
    for category_abj in category_all:
        category_dict = category_abj.to_dict()
        categories.append(category_dict)
    # 拼接内容
    data = {
        "user":user,
        "news_dict":clicks_news_li,
        "categories":categories,
    }
    # 返回数据
    return render_template("new/index.html",data = data)


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """

    # 1. 获取参数,并指定默认为最新分类,第一页,一页显示10条数据
    try:
        cid = int(request.args.get('cid', "1"))
        page = int(request.args.get('page', "1"))
        print(cid,page)
    except:
        data = {
            'current_page': 1,
            'total_page': 1,
            'news_dict_list': [],
        }
        return jsonify( data = data,errno=RET.PARAMERR, errmsg="参数类型异常")

    # 2. 校验参数
    if not all([cid, page]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    filter = [News.status == 0]
    if cid != 1:
        filter.append(News.category_id == cid)

    # 3. 查询数据
    paginate = News.query.order_by(News.create_time.desc()).paginate(page, constants.HOME_PAGE_MAX_NEWS, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    # 将模型对象列表转成字典列表
    news_dict_list =[]
    for item in items:
        news_dict_list.append(item.to_dict())
    data = {
        'categories':current_page,
        'total_page':total_page,
        'news_dict_list':news_dict_list,
    }
    #返回数据
    return jsonify(errno = RET.OK,errmsg = 'OK',data = data)