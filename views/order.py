from datetime import datetime
from flask import Blueprint, jsonify, request  # 导入 Blueprint 和 jsonify 模块
from models import db
from models import Order  # 导入 Order 模型

bp = Blueprint('order', __name__)  # 创建名为 'order' 的蓝图

@bp.route('/api/v1/my_orders/<int:user_id>', methods=['GET'])  # 定义路由和请求方法
def my_orders(user_id):  # 定义视图函数
    orders = Order.query.filter_by(user_id=user_id).all()  # 查询指定用户的订单
    order_list = []  # 初始化订单列表
    for order in orders:  # 遍历订单
        order_data = {  # 构造订单数据字典
            'order_id': order.order_id,  # 订单 ID
            'total_price': str(order.total_price),  # 总价
            'payment_status': order.payment_status,  # 支付状态
            'created_at': str(order.created_at)  # 创建时间
        }
        order_list.append(order_data)  # 将订单数据添加到列表中
    return jsonify({'orders': order_list})  # 返回 JSON 格式的订单列表


@bp.route('/api/v1/order/new', methods=['POST'])  # 定义路由和请求方法
def create_order():
    data = request.get_json()  # 获取请求中的 JSON 数据

    # 提取请求数据中的必要字段
    user_id = data.get('user_id')
    total_price = data.get('total_price')

    # 检查是否提供了必要的数据
    if not user_id or not total_price:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # 创建新订单对象
        new_order = Order(
            user_id=user_id,
            total_price=total_price,
            created_at=datetime.utcnow()  # 设置订单创建时间
        )

        # 将新订单添加到数据库
        db.session.add(new_order)
        db.session.commit()  # 提交事务保存数据

        # 返回新创建订单的相关信息
        return jsonify({
            'message': 'Order created successfully',
            'order': {
                'order_id': new_order.order_id,
                'user_id': new_order.user_id,
                'total_price': str(new_order.total_price),
                'payment_status': new_order.payment_status,
                'created_at': str(new_order.created_at)
            }
        }), 201  # 状态码 201 表示资源成功创建
    except Exception as e:
        db.session.rollback()  # 如果出现错误，回滚事务
        return jsonify({'error': str(e)}), 500  # 返回错误信