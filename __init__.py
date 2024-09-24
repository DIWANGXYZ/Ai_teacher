from flask import Flask  # 导入 Flask 模块
from celery import Celery  # 导入 Celery 模块
from models import db
celery = Celery(__name__)  # 初始化 Celery

def create_app(config_class='Ai_teacher.config.Config'):
    app = Flask(__name__)  # 创建 Flask 应用实例

    # 加载配置
    app.config.from_object(config_class)  # 从指定的配置类加载配置

    # 初始化数据库
    db.init_app(app)  # 初始化 SQLAlchemy 数据库

    # 初始化 Celery 配置
    celery.conf.update(app.config)  # 更新 Celery 的配置

    # 初始化蓝图
    from .views import order, payment, product, purchased_book, user  # 导入蓝图模块
    app.register_blueprint(order.bp)  # 注册订单蓝图
    app.register_blueprint(payment.bp)  # 注册支付蓝图
    app.register_blueprint(product.bp)  # 注册产品蓝图
    app.register_blueprint(purchased_book.bp)  # 注册已购书籍蓝图
    app.register_blueprint(user.bp)  # 注册用户蓝图

    return app  # 返回创建的应用实例
