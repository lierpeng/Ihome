#coding=utf-8
from flask import Blueprint,session,make_response,jsonify,request,current_app
user_blueprint = Blueprint('user',__name__)
from captcha.captcha import captcha
from ytx_sdk.ytx_send import sendTemplateSMS
from status_code import ret_map,RET
import re
from models import User
import random
import logging
from qiniu import put_data,Auth
from decorators.my_decoraters import is_login


@user_blueprint.route('/yzm')
def yzm():
    name,text,image = captcha.generate_captcha()
    session['image_yzm'] = text
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@user_blueprint.route('/send_sms')
def send_sms():
    dict=request.args
    mobile = dict.get('mobile')
    imageCode=dict.get('imageCode')

    if not all([mobile,imageCode]) :
        return jsonify(code=RET.PARAMERR,msg=ret_map[RET.PARAMERR])

    #1手机号
    if not re.match('^1[345789]\d{9}',mobile):
        return jsonify(code=RET.PARAMERR,msg=u'手机号错误')

    #1.1
    if User.query.filter_by(phone=mobile).count():
        return jsonify(code=RET.PARAMERR, msg=u'手机号存在')
    #验证码
    #图片验证码
    if imageCode != session['image_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'图片验证码错误')
    sms_code = random.randint(1000,9999)
    session['sms_yzm'] = sms_code
    print sms_code
    # result = sendTemplateSMS('phone',[sms_code,5],1)
    result = '000000'
    if result=='000000':
        return jsonify(code=RET.OK,msg=ret_map[RET.OK])
    else:
        return jsonify(code=RET.UNKOWNERR,msg=ret_map[RET.UNKOWNERR])

@user_blueprint.route('/',methods=['POST'])
def user_register():
    #接收参数
    dict = request.form

    mobile = dict.get('mobile')
    imagecode = dict.get('imagecode')
    phonecode = dict.get('phonecode')
    password = dict.get('password')
    password2 = dict.get('password2')
   #验证码参数是否存在
    if not all([mobile,imagecode,phonecode,password,password2]):
        return jsonify(code=RET.PARAMERR,msg=ret_map[RET.PARAMERR])

    if imagecode!=session['image_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'图片验证码错误')

   #验证短信验证码
    if int(phonecode)!=session['sms_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'手机验证码错误')
   #手机格式是否正确
    if not re.match('^1[345789]\d{9}',mobile):
         return jsonify(code=RET.PARAMERR,msg=u'手机号错误')
    if User.query.filter_by(phone=mobile).count():
        return jsonify(code=RET.PARAMERR, msg=u'手机号存在')

    #保存对象
    user = User()
    user.phone = mobile
    user.name = mobile
    user.password = password

    try:
        user.add_update()
        return jsonify(code=RET.OK,msg=ret_map[RET.OK])
    except:
        logging.ERROR(u'用户注册更新数据库失败,手机号%s,密码%s'%(mobile,password))
        return jsonify(code=RET.DBERR,msg=ret_map[RET.DBERR])

@user_blueprint.route('/',methods=["GET"])
@is_login
def user_my():
    #获取当前用户
    user_id=session['user_id']
    #查询当前用户头像..
    user = User.query.get(user_id)
    return jsonify(user=user.to_basic_dict())

@is_login
@user_blueprint.route('/auth',methods=['GET'])
def user_auth():
    user_id=session['user_id']
    user=User.query.get(user_id)
    return jsonify(user.to_auth_dict())

@is_login
@user_blueprint.route('/auth',methods=['PUT'])
def user_auth_set():
    #接受参数
    dict=request.form
    id_name = dict.get('id_name')
    id_card=dict.get('id_card')
    #验证参数的有效性
    if not all([id_name,id_card]):
        return jsonify(code=RET.PARAMERR,msg=ret_map[RET.PARAMERR])

    if not re.match(r'^[1-9]\d{5}(19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',id_card):
        return jsonify(code=RET.PARAMERR,msg=ret_map[RET.PARAMERR])
    try:
       user = User.query.get(session['user_id'])
    except:
        logging.ERROR('查询用户失败')
        return jsonify(code=RET.DBERR)
    try:
       user.id_card=id_card
       user.id_name=id_name
       user.add_update()
    except:
        logging.ERROR(u'修改用户姓名、身份证号失败')
        return jsonify(code=RET.DBERR)
    #返回数据
    return jsonify(code=RET.OK)

@is_login
@user_blueprint.route('/',methods=['PUT'])
def user_profile():
    dict=request.form
    if 'avatar1' in dict:
        try:
            #上传头像
            f1 = request.files['avatar']
            """
            mime-type:国际规范,表示文件类型,如text/html,image/jpeg
            """
            # if not re.match('image/.*',f1.mimetype):
            #     return jsonify(code=RET.PARAMERR)

        except:
            return jsonify(code=RET.PARAMERR)
        # 上传到七牛云
        access_key = 'VkuPJBo4rAwXFSzfOZldfpt6vKv3yzFxRKUJyuVQ'
        secret_key = 'JZ__SUwrXJEhaas19E7k91x5KaVbMMIoERw1Q4Rt'
        # 空间名称
        bucket_name = 'flask-lhy'
        try:
            # 构建鉴权对象
            q = Auth(access_key, secret_key)
            # 生成上传 Token
            token = q.upload_token(bucket_name)
            # 上传文件数据，ret是字典，键为hash、key，值为新文件名，info是response对象
            ret, info = put_data(token, None, f1.read())
        except:
            logging.ERROR(u'访问七牛云出错')
            return jsonify(code=RET.SERVERERR)

        try:
            user = User.query.get(session['user_id'])
            user.avator = ret.get('key')
            user.add_update()

        except:
            logging.ERROR(u'数据库访问失败')
            return jsonify(code=RET.DBERR)
        return jsonify(code=RET.OK,url=current_app.config['QINIU_URL']+ret.get('key'))

    elif 'name' in dict:
        #修改用户名
        name=dict.get('name')
        if User.query.filter_by(name=name).count():
            return jsonify(code=RET.DATAEXIST)
        else:
            user=User.query.get(session['user_id'])
            user.name=name
            user.add_update()
            return jsonify(code=RET.OK)
    else:
        return jsonify(code=RET.PARAMERR,msg=ret_map[RET.PARAMERR])

@user_blueprint.route('/session',methods=['POST'])
def user_login():
    dict = request.form
    mobile=dict.get('mobile')
    password=dict.get('password')
    if not all([mobile,password]):
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])

    if not re.match('^1[345789]\d{9}',mobile):
         return jsonify(code=RET.PARAMERR,msg=u'手机号错误')
    try:
       user = User.query.filter_by(phone=mobile).first()

    except:
        logging.ERROR(u'用户登陆---数据库出错')
        return jsonify(code=RET.DBERR, msg=ret_map[RET.DBERR])

    if user:
        if user.check_pwd(password):
           session['user_id']=user.id
           return jsonify(code=RET.OK,msg=ret_map[RET.OK])
        else:
           return jsonify(code=RET.PARAMERR,msg=u"密码错误")

    else:
        return jsonify(code=RET.PARAMERR, msg=u'手机号不存在')

@user_blueprint.route('/session',methods=['GET'])
@is_login
def user_is_login():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return jsonify(code=RET.OK,name=user.name)

@user_blueprint.route('/session',methods=['DELETE'])
def user_logout():
    del session['user_id']
    return jsonify(code=RET.OK)


