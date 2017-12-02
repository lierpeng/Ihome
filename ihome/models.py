#coding=utf-8
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
db = SQLAlchemy()

class BaseModel(object):
    create_time = db.Column(db.DATETIME,default=datetime.now())
    update_time = db.Column(db.DATETIME,default=datetime.now(),onupdate=datetime.now())

    def add_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(BaseModel,db.Model):
    __tablename__ = 'ihome_user'
    id = db.Column(db.Integer,primary_key=True)
    phone=db.Column(db.String(11),unique=True)
    pwd_hash = db.Column(db.String(200))
    name = db.Column(db.String(30),unique=True)
    avator=db.Column(db.String(100))
    id_name = db.Column(db.String(30))
    id_card = db.Column(db.String(18),unique=True)
    #du
    @property
    def password(self):
        return ''


    @password.setter
    def password(self,pwd):
        self.pwd_hash=generate_password_hash(pwd)

    #duibi
    def check_pwd(self,pwd):
        return check_password_hash(self.pwd_hash,pwd)

    def to_basic_dict(self):
        return {
            'id':self.id,
            'avatar':current_app.config["QINIU_URL"]+self.avator if self.avator else self.avator,
            'name':self.name,
            'phone':self.phone
        }

    def to_auth_dict(self):
        return{
            'id_name':self.id_name,
            'id_card':self.id_card
        }