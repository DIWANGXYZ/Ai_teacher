from celery import Celery  # 导入 Celery 模块
from .. import create_app  # 导入 create_app 函数

app = create_app()  # 创建 Flask 应用实例

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])  # 创建 Celery 实例，并设置 Broker URL
celery.conf.update(app.config)  # 更新 Celery 的配置项，使其与 Flask 应用的配置一致
