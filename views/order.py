
from flask import Blueprint, jsonify  # 导入 Blueprint 和 jsonify 模块
from ..models import Order  # 导入 Order 模型

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

@bp.route('/api/v1/order/new', methods=['POST'])
def create_order():

    return jsonify({'order_id': 'xxxx'})