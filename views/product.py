from flask import Blueprint, jsonify  # 导入 Blueprint 和 jsonify 模块
from ..models import Product  # 导入 Product 模型

bp = Blueprint('product', __name__)  # 创建名为 'product' 的蓝图

# 定义路由和请求方法
@bp.route('/api/v1/products', methods=['GET'])
def get_products():
    products = Product.query.all()  # 查询所有产品
    product_list = []  # 初始化产品列表
    for product in products:  # 遍历所有产品
        product_data = {  # 构造产品数据字典
            'id': product.id,  # 产品 ID
            'bookurl': product.bookurl,  # 产品 URL
            'ver': product.ver,  # 版本号
            'price': str(product.price),  # 原价
            'type': product.type,  # 类型
            'bookname': product.bookname,  # 书名
            'discount_price': str(product.discount_price),  # 折扣价
            'description': product.description  # 描述
        }
        product_list.append(product_data)  # 将产品数据添加到列表中
    return jsonify({'products': product_list})  # 返回 JSON 格式的列表
