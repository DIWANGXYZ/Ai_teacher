from flask import Blueprint  # 导入 Blueprint 类

bp = Blueprint('order', __name__)  # 创建名为 'order' 的蓝图

from . import order  # 导入 order 模块
