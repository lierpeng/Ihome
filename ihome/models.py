from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class BaseModel(object):
    create_time = db.Column(db.DATETIME,default=datetime.now())
    update_time = db.Column(db.DATETIME,default=datetime.now(),onupdate=datetime.now())

