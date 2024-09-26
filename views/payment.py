import json
import logging
from datetime import datetime  # 导入 datetime 模块
import requests  # 导入 requests 模块
from flask import Blueprint, request, jsonify  # 导入 Flask 相关模块
import base64  # 导入base64模块
from models import Order, db  # 导入 Order 模型
from utils import generate_nonce_str, generate_rsa_sign, build_message, generate_authorization_header, \
    load_private_key, load_public_key, generate_out_trade_no  # 导入工具函数

bp = Blueprint('payment', __name__)  # 创建名为 'payment' 的蓝图

private_key = load_private_key()
public_key = load_public_key()

from config import Config

# 在调用函数前设置全局变量
WECHAT_APPID = Config.WECHAT_APPID
WECHAT_MCH_ID = Config.WECHAT_MCH_ID
WECHAT_NOTIFY_URL = Config.WECHAT_NOTIFY_URL
WECHAT_UNIFIED_ORDER_URL = Config.WECHAT_UNIFIED_ORDER_URL
WECHAT_SERIAL_NO = Config.WECHAT_SERIAL_NO
WECHAT_API_KEY = Config.WECHAT_API_KEY

@bp.route('/api/v1/user/book/purchase', methods=['POST'])
def purchase_book():
    data = request.get_json()
    products = data.get('products')
    uid = data.get('uid')
    pay_src = data.get('pay_src')
    type = data.get('type')

    # 参数验证
    if not products or not isinstance(products, list):
        return jsonify({'code': 1, 'msg': '产品信息不正确'}), 400

    for product in products:
        if '_id' not in product or 'price' not in product:
            return jsonify({'code': 1, 'msg': '每个产品必须包含 _id 和 price'}), 400

    if not uid or not pay_src or type not in ['book', 'vip']:
        return jsonify({'code': 1, 'msg': '请求参数不完整'}), 400

    # 处理订单逻辑
    try:
        total_fee = sum(product['price'] for product in products)  # 计算总费用
        order_id = generate_out_trade_no(uid)  # 根据用户 ID 生成订单号

        # 创建订单记录
        new_order = Order(
            order_id=order_id,
            user_id=uid,
            total_price=total_fee,
            created_at=datetime.utcnow()  # 设置订单创建时间
        )

        # 将新订单添加到数据库
        db.session.add(new_order)
        db.session.commit()  # 提交事务保存数据

        # 发送微信支付请求
        payment_response, status_code = wechat_unified_order_app(order_id, total_fee, '书籍购买')

        if payment_response['code'] != 0:
            db.session.rollback()  # 如果支付请求失败，回滚订单
            return jsonify(payment_response), status_code


        return jsonify({
            'code': 0,
            'msg': '订单创建成功',
            'data': payment_response['data']}), 201

    except Exception as e:
        db.session.rollback()  # 回滚事务
        return jsonify({'code': 1, 'msg': f'处理订单时出错: {str(e)}'}), 500


def wechat_unified_order_app(uid, total_fee, product_description):
    try:
        out_trade_no = generate_out_trade_no(uid)
        logging.debug(f"Generated out_trade_no: {out_trade_no}")

        payload = {
            'appid': WECHAT_APPID,
            'mchid': WECHAT_MCH_ID,
            'description': product_description,
            'out_trade_no': out_trade_no,
            'amount': {'total': int(total_fee), 'currency': 'CNY'},
            'notify_url': WECHAT_NOTIFY_URL
        }

        nonce_str = generate_nonce_str()
        timestamp = str(int(datetime.now().timestamp()))
        http_method = 'POST'
        url = '/v3/pay/transactions/app'
        body = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

        sign_message = build_message(http_method, url, timestamp, nonce_str, body)
        logging.debug(f"Sign message: {sign_message}")

        signature = generate_rsa_sign(sign_message, private_key)
        logging.debug(f"Signature: {base64.b64encode(signature).decode()}")
        authorization_header = generate_authorization_header(WECHAT_MCH_ID, nonce_str, signature, WECHAT_SERIAL_NO, timestamp)

        headers = {
            'Authorization': authorization_header,
            'Content-Type': 'application/json'
        }

        response = requests.post(WECHAT_UNIFIED_ORDER_URL, data=body, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            prepay_id = result.get("prepay_id")
            pay_sign_message = build_message('GET', f'/v3/pay/transactions/id/{prepay_id}', timestamp, nonce_str, '')
            pay_sign = generate_rsa_sign(pay_sign_message, private_key)

            return {
                'code': 0,
                'msg': 'ok',
                'data': {
                    'appid': WECHAT_APPID,
                    'partnerid': WECHAT_MCH_ID,
                    'prepayid': prepay_id,
                    'package': 'Sign=WXPay',
                    'noncestr': nonce_str,
                    'timestamp': timestamp,
                    'sign': base64.b64encode(pay_sign).decode()
                }
            }, 200  # 返回字典和状态码

        else:
            return {'code': 1, 'msg': 'Unified order request failed', 'detail': response.text}, response.status_code

    except Exception as e:
        return {'code': 1, 'msg': str(e)}, 500
