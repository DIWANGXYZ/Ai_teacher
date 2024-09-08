from celery import Celery
from app import app


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker='redis://localhost:6379/0',  # 使用 Redis 作为消息代理
        backend='redis://localhost:6379/0'  # 设置 Celery 的结果存储
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)
