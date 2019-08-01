from flask import session, jsonify, current_app, render_template, request, g

from info.models import User, News, Category
from info.utils import constants
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu


# 测试

@index_blu.route('/')
@user_login_data
def index():
    # 获取到当前登录用户的id
    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 使用g变量获取用户登陆信息
    user = g.user

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
        "category_list":categories,
    }
    # 返回数据
    return render_template("news/index.html",data = data)


@index_blu.route('/news_list')
def news_list(category_id=None):
    """
    获取首页新闻数据
    :return:
    """

    # 1. 获取参数,并指定默认为最新分类,第一页,一页显示10条数据
    cid = request.args.get('cid', 1)
    page = request.args.get('page', 1)


    # 2. 校验参数
    if not all([cid, page]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')

    try:
        cid = int(cid)
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
    filter_list = [News.status == 0]

    if cid != 1:
        filter_list.append(News.category_id == cid)
        
        
    # 3. 查询数据并分页
    
    filters = [News.status == 0]
    # 如果分类id不为0，那么添加分类id的过滤
    if category_id != "0":
        filters.append(News.category_id == category_id)

    # 4. 查询数据
    pn = []
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(page, constants.HOME_PAGE_MAX_NEWS)
    except BaseException as e:
        current_app.logger.error(e)
    data = {
        "news_dict_list": [news.to_dict() for news in pn.items],
        "total_page": pn.pages,
        "cur_page":pn.page,
    }

    return jsonify(errno = RET.OK,errmsg = 'OK',data = data)