from flask import Flask
from manager import create_app

from config import DevelopConfig
app = create_app(DevelopConfig)

from models import db
db.init_app(app)


from flask_script import Manager
manager = Manager(app)

from flask_migrate import Migrate,MigrateCommand
Migrate(app,db)
manager.add_command('db',MigrateCommand)


from html_views import html_blueprint
app.register_blueprint(html_blueprint)

from api_v1.house_views import house_blueprint
app.register_blueprint(house_blueprint,url_prefix='/api/v1/house')

from api_v1.order_views import order_blueprint
app.register_blueprint(order_blueprint,url_prefix='/api/v1/order')

from api_v1.user_views import user_blueprint
app.register_blueprint(user_blueprint,url_prefix='/api/v1/user')


if __name__ == '__main__':
    manager.run()
