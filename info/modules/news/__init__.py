from flask import Blueprint

# 创建蓝图对象
news_detail = Blueprint('news', __name__,url_prefix="/news")

from . import  views