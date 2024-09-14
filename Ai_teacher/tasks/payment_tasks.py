from .. import celery, db
from ..models import Order
from ..utils import verify_signature
import logging  # 增加日志

# 定义异步任务处理微信回调
@celery.task(bind=True, max_retries=3)  # 定义Celery任务，处理微信支付回调
def process_wechat_callback(self, callback_data):  # 定义处理微信回调的函数
    try:
        # 校验回调数据是否完整
        if not all(key in callback_data for key in ('sign', 'id', 'event_type', 'resource')):
            return {'message': 'Invalid callback data'}, 400  # 缺少字段时，返回错误信息

        sign = callback_data.get('sign')  # 获取签名
        message = f"{callback_data['id']}\n{callback_data['event_type']}\n{callback_data['resource']['ciphertext']}\n"  # 构造待验证的消息

        # 验证签名
        try:
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
            logging.error(f"Error during signature verification: {e}")  # 记录签名验证错误日志
            return {'message': 'Signature verification failed'}, 400  # 返回失败信息

    except Exception as e:
        logging.error(f"Error processing WeChat callback: {e}")  # 记录错误日志
        self.retry(exc=e, countdown=60)  # 重试任务
        return {'error': 'Server error'}, 500  # 返回服务器错误信息



