import base64  # 导入 base64 模块
from datetime import time  # 导入 time 模块

import requests  # 导入 requests 模块
from flask import Blueprint, request, jsonify  # 导入 Flask 相关模块

from ..models import Order  # 导入 Order 模型
from ..utils import generate_nonce_str, generate_rsa_sign, build_message, generate_authorization_header  # 导入工具函数

bp = Blueprint('payment', __name__)  # 创建名为 'payment' 的蓝图

WECHAT_APPID = 'wx61747d31a0c20812'  # 微信 APP 的 AppID
WECHAT_MCH_ID = '1592365211'  # 微信支付的商户号
WECHAT_API_KEY = 'e820c835dda6afb4a3f902ed7ffba6b7'  # 微信支付的 API 密钥
WECHAT_UNIFIED_ORDER_URL = 'https://api.mch.weixin.qq.com/v3/pay/transactions/app'  # 微信支付 APP 场景的下单接口 URL
WECHAT_NOTIFY_URL = 'https://www.duoduozhijiao.cn/notify'  # 微信支付异步通知回调 URL
WECHAT_SERIAL_NO = '46A85E6C5BDE0CB76B1EB839FFAEC8FFEE6A5AD7'  # 微信支付证书的序列号

# 定义路由和请求方法
@bp.route('/api/v1/payment/wechat', methods=['POST'])
def wechat_unified_order_app():
    data = request.get_json()  # 获取请求中的 JSON 数据
    order_id = data.get('order_id')  # 获取订单 ID
    total_fee = data.get('total_fee')  # 获取总费用
    product_description = data.get('description')  # 获取商品描述

    try:
        order = Order.query.get(order_id)  # 查询订单
        payload = {  # 构造支付请求参数
            'appid': WECHAT_APPID,
            'mchid': WECHAT_MCH_ID,
            'description': product_description,
            'out_trade_no': str(order_id),
            'amount': {'total': int(total_fee), 'currency': 'CNY'},
            'notify_url': WECHAT_NOTIFY_URL
        }

        nonce_str = generate_nonce_str()  # 生成随机字符串
        timestamp = str(int(time.time()))  # 生成时间戳
        signature = generate_rsa_sign(build_message(WECHAT_APPID, timestamp, nonce_str, ""))  # 生成签名
        authorization_header = generate_authorization_header(WECHAT_MCH_ID, nonce_str, signature, WECHAT_SERIAL_NO)  # 生成授权头

        headers = {  # 构造请求头
            'Authorization': authorization_header,
            'Content-Type': 'application/json'
        }

        response = requests.post(WECHAT_UNIFIED_ORDER_URL, json=payload, headers=headers, timeout=30)  # 发送支付请求

        if response.status_code == 200:  # 如果响应状态码为 200
            result = response.json()  # 解析响应结果
            prepay_id = result.get("prepay_id")  # 获取预支付 ID
            pay_sign_message = build_message(WECHAT_APPID, timestamp, nonce_str, prepay_id)  # 构造支付签名消息
            pay_sign = generate_rsa_sign(pay_sign_message)  # 生成支付签名

            return jsonify({  # 返回 APP 支付所需的数据
                'appid': WECHAT_APPID,
                'partnerid': WECHAT_MCH_ID,
                'prepayid': prepay_id,
                'package': 'Sign=WXPay',
                'noncestr': nonce_str,
                'timestamp': timestamp,
                'sign': base64.b64encode(pay_sign).decode()
            })
        else:
            return jsonify({'error': 'Unified order request failed'}), response.status_code  # 返回错误信息

    except Exception as e:  # 捕获异常
        return jsonify({'error': str(e)}), 500  # 返回异常信息
