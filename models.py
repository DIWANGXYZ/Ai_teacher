from Ai_teacher import db  # 导入数据库模块
from datetime import datetime  # 导入日期时间模块

# 定义产品模型
class Product(db.Model):
    __tablename__ = 'products'  # 设置表名为 products
    id = db.Column('product_id', db.Integer, nullable=False, primary_key=True)  # 主键
    bookurl = db.Column(db.String(255))  # 书籍URL
    ver = db.Column(db.Text)  # 版本信息
    price = db.Column(db.Numeric(10, 2))  # 原价
    type = db.Column(db.String(255))  # 类型
    bookname = db.Column(db.String(255))  # 书名
    discount_price = db.Column(db.Numeric(10, 2))  # 折扣价
    description = db.Column(db.String(255))  # 描述

# 定义用户模型
class User(db.Model):
    __tablename__ = 'users'  # 设置表名为 users
    user_id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键
    username = db.Column(db.String(255))  # 用户名
    email = db.Column(db.String(255))  # 邮箱
    password = db.Column(db.String(255))  # 密码
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 创建时间，默认为当前时间

    def __repr__(self):
        return f'<User {self.username}>'  # 返回用户的字符串表示形式

# 定义订单模型
class Order(db.Model):
    __tablename__ = 'orders'  # 设置表名为 orders
    order_id = db.Column(db.Integer, primary_key=True)  # 订单ID，主键
    total_price = db.Column(db.Numeric(10, 2))  # 总价
    payment_price = db.Column(db.Numeric(10, 2))  # 实付金额
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 用户ID，外键关联用户表
    payment_status = db.Column(db.String(255))  # 支付状态
    transaction_id = db.Column(db.String(255))  # 交易ID
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 创建时间，默认为当前时间
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，默认为当前时间，并在更新时更新

# 定义订单项模型
class OrderItem(db.Model):
    __tablename__ = 'order_items'  # 设置表名为 order_items
    id = db.Column(db.Integer, primary_key=True)  # ID，主键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)  # 订单ID，外键关联订单表
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # 产品ID，外键关联产品表
    quantity = db.Column(db.Integer, nullable=False)  # 数量
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 单价
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)  # 折扣价

# 定义已购书籍模型
class PurchasedBook(db.Model):
    __tablename__ = 'purchased_books'  # 设置表名为 purchased_books
    id = db.Column(db.Integer, primary_key=True)  # ID，主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 用户ID，外键关联用户表
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # 产品ID，外键关联产品表
    purchase_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # 购买时间，默认为当前时间
    amount = db.Column(db.Integer, nullable=False)  # 购买数量
