#coding=utf-8
import redis
import hashlib
class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI='mysql://root:mysql@127.0.0.1:3306/ihome_bj14'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session配置
    SECRET_KEY = "iHome"
    # 将session存储到redis中
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14  # 秒
    #囚牛云的访问服务器
    QINIU_URL = 'http://p00zz5i01.bkt.clouddn.com/'

    TOKEN=hashlib.md5('ihome_bj14').hexdigest()

class DevelopConfig(Config):
    DEBUG = True

class ProductConfig(Config):
    pass