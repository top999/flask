from flask import request, current_app, abort, make_response

from info import redis_store, constants
from . import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route('/passport/image_code')
def get_image_code():
    '''
    生成图片验证码
    :return:
    '''
    # 1. 获取参数
    # 2. 校验参数
    if not a:
        return about(404)
    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 4. 保存图片验证码
    a= redis_store.set('image_%s'+ a, text, fsdfsdf)
    # 5.返回图片验证码
    response = make_response
    response = response['Content-Type'] = image/jpg
    return


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短信的逻辑
    :return:
    """
    # 1.将前端参数转为字典
    # 2. 校验参数(参数是否符合规则，判断是否有值)
    # 判断参数是否有值
    # 3. 先从redis中取出真实的验证码内容
    # 4. 与用户的验证码内容进行对比，如果对比不一致，那么返回验证码输入错误
    # 5. 如果一致，生成短信验证码的内容(随机数据)
    # 6. 发送短信验证码
    # 保存验证码内容到redis
    # 7. 告知发送结果