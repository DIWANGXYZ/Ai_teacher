import logging  # 导入日志模块
from flask import Flask, request, jsonify  # 导入Flask相关模块
from celery import Celery  # 导入Celery模块
from flask_sqlalchemy import SQLAlchemy  # 导入SQLAlchemy模块
from datetime import datetime  # 导入datetime模块
import requests  # 导入requests模块
import random  # 导入random模块
import string  # 导入string模块
import time  # 导入time模块
import base64  # 导入base64模块
from cryptography.hazmat.primitives import hashes  # 导入hashes模块
from cryptography.hazmat.primitives.asymmetric import padding  # 导入padding模块
from cryptography.hazmat.primitives import serialization  # 导入serialization模块

app = Flask(__name__)  # 创建Flask应用实例

# 配置 Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])  # 初始化Celery实例
celery.conf.update(app.config)  # 更新Celery配置

# PostgreSQL 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/Ai_teacher'  # 设置数据库URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用修改追踪

db = SQLAlchemy(app)  # 初始化SQLAlchemy实例


# 定义商品的数据库模型
class Product(db.Model):  # 定义Product类
    __tablename__ = 'products'  # 设置表名
    id = db.Column('product_id', db.Integer, nullable=False, primary_key=True)  # 设置主键
    bookurl = db.Column(db.String(255))  # 设置bookurl字段
    ver = db.Column(db.Text)  # 设置ver字段
    price = db.Column(db.Numeric(10, 2))  # 设置price字段
    type = db.Column(db.String(255))  # 设置type字段
    bookname = db.Column(db.String(255))  # 设置bookname字段
    discount_price = db.Column(db.Numeric(10, 2))  # 设置discount_price字段
    description = db.Column(db.String(255))  # 设置description字段


# 定义用户的数据库模型
class User(db.Model):  # 定义User类
    __tablename__ = 'users'  # 设置表名
    user_id = db.Column(db.Integer, primary_key=True)  # 设置主键
    username = db.Column(db.String(255))  # 设置username字段
    email = db.Column(db.String(255))  # 设置email字段
    password = db.Column(db.String(255))  # 设置password字段
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 设置created_at字段

    def __repr__(self):  # 定义对象表示方法
        return f'<User {self.username}>'  # 返回用户字符串表示


# 定义订单的数据库模型
class Order(db.Model):  # 定义Order类
    __tablename__ = 'orders'  # 设置表名
    order_id = db.Column(db.Integer, primary_key=True)  # 设置主键
    total_price = db.Column(db.Numeric(10, 2))  # 设置total_price字段
    payment_price = db.Column(db.Numeric(10, 2))  # 设置payment_price字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 设置外键
    payment_status = db.Column(db.String(255))  # 设置payment_status字段
    transaction_id = db.Column(db.String(255))  # 设置transaction_id字段
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 设置created_at字段
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)  # 设置updated_at字段


# 定义订单项的数据库模型
class OrderItem(db.Model):  # 定义OrderItem类
    __tablename__ = 'order_items'  # 设置表名
    id = db.Column(db.Integer, primary_key=True)  # 设置主键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)  # 设置外键
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # 设置外键
    quantity = db.Column(db.Integer, nullable=False)  # 设置quantity字段
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 添加 price 字段, 存储订单商品的原始价格
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)  # 添加 discount_price 字段, 存储订单商品的折后价格



# 定义已购书籍的数据库模型
class PurchasedBook(db.Model):  # 定义PurchasedBook类
    __tablename__ = 'purchased_books'  # 设置表名
    id = db.Column(db.Integer, primary_key=True)  # 设置主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 设置外键
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # 设置外键
    purchase_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 设置purchase_date字段
    amount = db.Column(db.Integer, nullable=False)  # 设置amount字段


with app.app_context():  # 在应用上下文中创建所有表
    db.create_all()  # 创建数据库中的所有表

    # 微信支付配置
    WECHAT_APPID = 'your_wechat_appid'  # 微信AppID
    WECHAT_MCH_ID = 'your_wechat_mch_id'  # 微信商户ID
    WECHAT_API_KEY = 'your_wechat_api_key'  # 微信API密钥
    WECHAT_UNIFIED_ORDER_URL = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'  # 微信统一下单接口URL
    WECHAT_ORDER_QUERY_URL = 'https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no'  # 微信订单查询接口URL
    WECHAT_NOTIFY_URL = 'https://your_domain.com/wechat_callback'  # 微信支付回调通知URL
    WECHAT_SERIAL_NO = 'your_certificate_serial_no'  # 微信证书序列号

    # 加载商户私钥用于签名
    with open('merchant_private_key.pem', 'rb') as key_file:  # 打开商户私钥文件
        private_key = serialization.load_pem_private_key(  # 加载商户私钥
            key_file.read(),  # 读取私钥内容
            password=None,  # 私钥没有密码
        )

    # 加载微信支付平台公钥用于验证签名
    with open('wechatpay_public_key.pem', 'rb') as key_file:  # 打开微信支付公钥文件
        public_key = serialization.load_pem_public_key(  # 加载微信支付平台的公钥
            key_file.read()  # 读取公钥内容
        )


    # 生成随机字符串，用于签名
    def generate_nonce_str():  # 定义生成随机字符串的函数
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))  # 生成32位随机字符串并返回


    # 生成SHA256 with RSA签名
    def generate_rsa_sign(message):  # 定义生成RSA签名的函数
        try:
            signature = private_key.sign(  # 使用私钥生成签名
                message.encode('utf-8'),  # 将消息编码为utf-8格式
                padding.PKCS1v15(),  # 使用PKCS1v15填充
                hashes.SHA256()  # 使用SHA256哈希算法
            )
            return signature  # 返回签名结果
        except Exception as e:
            logging.error(f"Error generating RSA signature: {e}")  # 记录生成签名时的错误日志
            raise  # 抛出异常


    # 验证签名
    def verify_signature(signature, message):  # 定义验证签名的函数
        try:
            public_key.verify(  # 使用公钥验证签名
                base64.b64decode(signature),  # 解码签名
                message.encode('utf-8'),  # 将消息编码为utf-8格式
                padding.PKCS1v15(),  # 使用PKCS1v15填充
                hashes.SHA256()  # 使用SHA256哈希算法
            )
            return True  # 如果验证成功，返回True
        except Exception as e:
            logging.error(f"Signature verification failed: {e}")  # 记录签名验证失败的错误日志
            return False  # 返回False


    # 构建待签名的消息字符串
    def build_message(appid, timestamp, nonce_str, prepay_id):  # 定义构建待签名消息的函数
        return f"{appid}\n{timestamp}\n{nonce_str}\n{prepay_id}\n"  # 按照微信支付要求的顺序构建签名字符串


    # 构造签名并生成Authorization请求头
    def generate_authorization_header(mchid, nonce_str, signature, serial_no):  # 定义生成授权头的函数
        timestamp = str(int(time.time()))  # 获取当前的时间戳
        authorization = (  # 构造Authorization头信息
            f'WECHATPAY2-SHA256-RSA2048 mchid="{mchid}",'  # mchid部分
            f'nonce_str="{nonce_str}",'  # 随机字符串部分
            f'signature="{base64.b64encode(signature).decode()}",'  # 签名部分
            f'timestamp="{timestamp}",'  # 时间戳部分
            f'serial_no="{serial_no}"'  # 证书序列号部分
        )
        return authorization  # 返回构建的授权头


    # 请求微信支付统一下单接口并签名
    @app.route('/wechat_unified_order', methods=['POST'])  # 定义处理微信支付统一下单的路由
    def wechat_unified_order():  # 定义处理微信统一下单请求的函数
        data = request.get_json()  # 从请求中获取JSON数据
        user_id = data.get('user_id')  # 获取用户ID
        order_id = data.get('order_id')  # 获取订单ID
        total_fee = data.get('total_fee')  # 获取总费用
        product_description = data.get('description')  # 获取商品描述
        openid = data.get('openid')  # 获取用户的微信OpenID

        try:
            order = Order.query.get(order_id)  # 从数据库中查询订单
            payload = {  # 构造微信支付的请求载荷
                'appid': WECHAT_APPID,  # 微信AppID
                'mchid': WECHAT_MCH_ID,  # 微信商户ID
                'description': product_description,  # 商品描述
                'out_trade_no': str(order_id),  # 商户订单号
                'amount': {'total': int(total_fee), 'currency': 'CNY'},  # 支付金额，单位为分
                'payer': {'openid': openid},  # 支付人的微信OpenID
                'notify_url': WECHAT_NOTIFY_URL  # 回调通知URL
            }

            # 生成随机字符串
            nonce_str = generate_nonce_str()  # 调用函数生成随机字符串
            # 获取当前时间戳
            timestamp = str(int(time.time()))  # 获取当前时间戳
            # 生成RSA签名
            signature = generate_rsa_sign(build_message(WECHAT_APPID, timestamp, nonce_str, ""))  # 生成签名
            # 构造授权头
            authorization_header = generate_authorization_header(WECHAT_MCH_ID, nonce_str, signature,
                                                                 WECHAT_SERIAL_NO)  # 生成授权头

            headers = {  # 定义请求头
                'Authorization': authorization_header,  # 授权头
                'Content-Type': 'application/json'  # 内容类型
            }

            # 请求微信统一下单接口
            response = requests.post(WECHAT_UNIFIED_ORDER_URL, json=payload, headers=headers, timeout=30)  # 发送请求

            if response.status_code == 200:  # 如果请求成功
                result = response.json()  # 获取返回的JSON结果
                prepay_id = result.get("prepay_id")  # 从结果中获取prepay_id

                # 生成用于支付的签名信息
                pay_sign_message = build_message(WECHAT_APPID, timestamp, nonce_str, prepay_id)  # 构造用于支付的消息
                pay_sign = generate_rsa_sign(pay_sign_message)  # 生成支付签名

                # 二次返回给APP需要的支付信息
                return jsonify({  # 构造返回的JSON数据
                    'appId': WECHAT_APPID,  # AppID
                    'timeStamp': timestamp,  # 时间戳
                    'nonceStr': nonce_str,  # 随机字符串
                    'package': f'prepay_id={prepay_id}',  # 微信支付package字段
                    'signType': 'RSA',  # 签名类型
                    'paySign': base64.b64encode(pay_sign).decode()  # 支付签名
                })
            else:
                return jsonify(
                    {'error': 'Unified order failed', 'response': response.text}), response.status_code  # 返回错误信息

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500  # 返回服务器内部错误


    # 定义异步任务处理微信回调
    @celery.task(bind=True, max_retries=3)  # 定义Celery任务，处理微信支付回调
    def process_wechat_callback(self, callback_data):  # 定义处理微信回调的函数
        try:
            sign = callback_data.get('sign')  # 获取签名
            message = f"{callback_data['id']}\n{callback_data['event_type']}\n{callback_data['resource']['ciphertext']}\n"  # 构造待验证的消息

            if verify_signature(sign, message):  # 验证签名
                if callback_data['event_type'] == 'TRANSACTION.SUCCESS':  # 如果交易成功
                    order_id = callback_data['out_trade_no']  # 获取订单ID
                    order = Order.query.get(order_id)  # 查询订单
                    if order:
                        order.payment_status = 'paid'  # 更新订单支付状态
                        db.session.commit()  # 提交更改
                        return {'message': 'Payment successful'}  # 返回成功信息
            return {'message': 'Signature verification failed or invalid callback data'}, 400  # 返回失败信息

        except Exception as e:
            self.retry(exc=e, countdown=60)  # 重试任务
            return {'error': 'Server error'}, 500  # 返回服务器错误信息


    # 我的课本接口
    @app.route('/my_books/<int:user_id>', methods=['GET'])
    def my_books(user_id):
        purchased_books = PurchasedBook.query.filter_by(user_id=user_id).all()  # 查询用户购买的书籍
        book_list = []  # 初始化书籍列表

        for purchased_book in purchased_books:  # 遍历购买记录
            product = Product.query.get(purchased_book.product_id)  # 查询书籍详情
            book_list.append({  # 添加书籍信息
                'bookname': product.bookname,
                'purchase_date': str(purchased_book.purchase_date),  # 使用 purchased_date 字段
                'amount': purchased_book.amount  # 新增的数量信息
            })

        return jsonify({'books': book_list})  # 返回书籍列表

    # 我的订单接口
    @app.route('/my_orders/<int:user_id>', methods=['GET'])
    def my_orders(user_id):
        orders = Order.query.filter_by(user_id=user_id).all()  # 查询用户的订单
        order_list = []  # 初始化订单列表
        for order in orders:  # 遍历订单
            order_data = {  # 构造订单数据
                'order_id': order.order_id,
                'total_price': str(order.total_price),
                'payment_status': order.payment_status,
                'created_at': str(order.created_at)
            }
            order_list.append(order_data)  # 添加订单数据

        return jsonify({'orders': order_list})  # 返回订单列表

    if __name__ == '__main__':
        app.run(debug=True)  # 启动应用