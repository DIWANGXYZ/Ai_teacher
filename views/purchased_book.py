from flask import Blueprint, jsonify  # 导入 Blueprint 和 jsonify 模块
from ..models import PurchasedBook  # 导入 PurchasedBook 模型

bp = Blueprint('purchased_book', __name__)  # 创建名为 'purchased_book' 的蓝图

# 定义路由和请求方法
@bp.route('/api/v1/users/<int:user_id>/books/', methods=['GET'])
def get_purchased_books(user_id):
    purchased_books = PurchasedBook.query.filter_by(user_id=user_id).all()  # 查询指定用户的已购书籍
    book_list = []  # 初始化书籍列表
    for book in purchased_books:  # 遍历所有已购书籍
        book_data = {  # 构造书籍数据字典
            'id': book.id,  # 书籍 ID
            'product_id': book.product_id,  # 产品 ID
            'purchase_date': str(book.purchase_date),  # 购买日期
            'amount': book.amount  # 数量
        }
        book_list.append(book_data)  # 将书籍数据添加到列表中
    return jsonify({'purchased_books': book_list})  # 返回 JSON 格式的书籍列表
