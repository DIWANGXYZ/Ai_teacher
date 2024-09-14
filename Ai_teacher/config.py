class Config:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Celery 的消息代理 URL，使用 Redis
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Celery 的结果存储后端，使用 Redis
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/Ai_teacher'  # SQLAlchemy 的数据库连接 URI，使用 PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 的修改跟踪功能
    WECHAT_APPID = 'ww318b83c9b073b30b'  # 微信公众号的 AppID
    WECHAT_MCH_ID = '1558863131'  # 微信支付的商户号
    WECHAT_API_KEY = '7HBEWIUWEFI27fhHJGJU823IURHH2FH2'  # 微信支付的 API 密钥
    WECHAT_UNIFIED_ORDER_URL = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'  # 微信支付统一下单接口 URL
    WECHAT_ORDER_QUERY_URL = 'https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no'  # 微信支付查询订单接口 URL
    WECHAT_NOTIFY_URL = 'https://qb.duoduozhijiao.cn/api/weixin/pay/onNotify'  # 微信支付异步通知回调 URL
    WECHAT_SERIAL_NO = 'your_certificate_serial_no'  # 微信支付证书的序列号
