# -*— coding:utf-8 -*—
from flask import Flask,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_message = '请先登录'
login_manager.login_view = '/login'

def create_app(config_name):
    # 创建 flask 实例
    app = Flask(__name__)
    # 从配置类中加载配置
    app.config.from_object(config[config_name])
    # 调用配置类中初始化函数，初始化app，这里该初始化函数为空
    config[config_name].init_app(app)

    # 初始化用到的各个模块（关联到当前app）
    bootstrap.init_app(app)
    db.init_app(app)
    db.app = app
    login_manager.init_app(app)

    # 注册蓝图(导入包初始化模块__init__中的内容时，需要加‘.’)
    from .main import main as main_bp
    from .reader import reader as reader_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(reader_bp,url_prefix='/reader')
    # 返回 flask 实例
    return app






