#coding=utf-8
from flask import Blueprint,session,make_response
user_blueprint = Blueprint('user',__name__)
from captcha.captcha import captcha

@user_blueprint.route('/yzm')
def yzm():
    name,text,image = captcha.generate_captcha()
    session['image_yzm'] = text
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

