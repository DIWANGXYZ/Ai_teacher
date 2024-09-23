from flask import Blueprint, jsonify  # 导入 Blueprint 和 jsonify 模块
from ..models import User  # 导入 User 模型

bp = Blueprint('user', __name__)  # 创建名为 'user' 的蓝图

# 定义路由和请求方法
@bp.route('api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)  # 查询指定用户 ID 的用户
    if user:  # 如果用户存在
        user_data = {  # 构造用户数据字典
            'user_id': user.user_id,  # 用户 ID
            'username': user.username,  # 用户名
            'email': user.email,  # 邮箱
            'created_at': str(user.created_at)  # 创建时间
        }
        return jsonify(user_data)  # 返回 JSON 格式的用户数据
    else:  # 如果用户不存在
        return jsonify({'error': 'User not found'}), 404  # 返回错误信息和状态码 404