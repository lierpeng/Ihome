#coding=utf-8
from flask import request,jsonify,current_app
from manager import create_app
from status_code import *
from config import DevelopConfig
app = create_app(DevelopConfig)

from models import db
db.init_app(app)

from html_views import html_blueprint
app.register_blueprint(html_blueprint)

from api_v1.house_views import house_blueprint
app.register_blueprint(house_blueprint,url_prefix='/api/v1/house')

from api_v1.order_views import order_blueprint
app.register_blueprint(order_blueprint,url_prefix='/api/v1/order')

from api_v1.user_views import user_blueprint
app.register_blueprint(user_blueprint,url_prefix='/api/v1/user')

from flask_script import Manager
manager = Manager(app)

from flask_migrate import Migrate,MigrateCommand
Migrate(app,db)
manager.add_command('db',MigrateCommand)

# @app.before_request
# def check_token():
#     if request.path.startwith('/api'):
#         if 'token' not in request.args or request.args.get("token") != current_app.config['TOKEN']:
#              return jsonify(code=RET.REQERR)

if __name__ == '__main__':
    manager.run()