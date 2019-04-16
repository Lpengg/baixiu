"""
app包主要包含所有的程序处理的相关文件(静态文件，模板文件，实体类以及各个业务包的处理)
__init__.py:
    1.构建Flask程序实例以及配置
    2.构建SQLAlchemy数据库实例
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# 声明SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 指定配置
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/baixiu'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SECRET_KEY'] = 'sessionConfig'

    # 关联db和app
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint)




    return app
