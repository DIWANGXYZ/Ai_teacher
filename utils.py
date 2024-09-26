import logging  # 导入日志模块
import os
import random  # 导入random模块
import string  # 导入string模块
import time  # 导入time模块
import base64  # 导入base64模块
from cryptography.hazmat.primitives import hashes  # 导入hashes模块
from cryptography.hazmat.primitives.asymmetric import padding  # 导入padding模块
from cryptography.hazmat.primitives import serialization  # 导入serialization模块

def load_private_key():
    # 获取当前脚本的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建相对路径
    key_path = os.path.join(current_dir, 'cret', 'apiclient_key.pem')

    with open(key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key


# 调用函数
private_key = load_private_key()


def load_public_key():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建相对路径
    key_path = os.path.join(current_dir, 'cret', 'public_key.pem')

    with open(key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
        )
    return public_key


# 生成随机字符串，用于签名
def generate_nonce_str():  # 定义生成随机字符串的函数
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))  # 生成32位随机字符串并返回


# 生成SHA256 with RSA签名
def generate_rsa_sign(message, private_key):  # 需要将私钥作为参数传递进来
    try:
        signature = private_key.sign(  # 使用私钥生成签名
            message.encode('utf-8'),  # 将消息编码为utf-8格式
            padding.PKCS1v15(),  # 使用PKCS1v15填充
            hashes.SHA256()  # 使用SHA256哈希算法
        )
        return signature  # 返回签名结果
    except Exception as e:
        logging.error(f"Error generating RSA signature: {e}")  # 记录生成签名时的错误日志
        raise  # 抛出异常


# 验证签名
def verify_signature(signature, message, public_key):  # 将公钥作为参数传递进来
    try:
        public_key.verify(  # 使用公钥验证签名
            base64.b64decode(signature),  # 解码签名
            message.encode('utf-8'),  # 将消息编码为utf-8格式
            padding.PKCS1v15(),  # 使用PKCS1v15填充
            hashes.SHA256()  # 使用SHA256哈希算法
        )
        return True  # 如果验证成功，返回True
    except Exception as e:
        logging.error(f"Signature verification failed: {e}")  # 记录签名验证失败的错误日志
        return False  # 返回False

# 生成符合要求的 out_trade_no
def generate_out_trade_no(uid):
    # 确保 out_trade_no 至少 6 个字符，并限制长度
    uid_part = str(uid)[:16]  # 截取 uid 的前 16 个字符
    timestamp_part = str(int(time.time()))  # 获取当前时间戳
    order_id = f"ORDER_{uid_part}_{timestamp_part}"  # 生成订单号
    return order_id[:32]  # 确保不超过 32 个字符

# 构建待签名的消息字符串
def build_message(http_method, url, timestamp, nonce_str, body):
    message = f"{http_method}\n{url}\n{timestamp}\n{nonce_str}\n{body}\n"
    return message


# 构造签名并生成Authorization请求头
def generate_authorization_header(mchid, nonce_str, signature, serial_no, timestamp):  # 定义生成授权头的函数
    authorization = (  # 构造Authorization头信息
        f'WECHATPAY2-SHA256-RSA2048 mchid="{mchid}",'  # mchid部分
        f'nonce_str="{nonce_str}",'  # 随机字符串部分
        f'signature="{base64.b64encode(signature).decode()}",'  # 签名部分
        f'timestamp="{timestamp}",'  # 时间戳部分
        f'serial_no="{serial_no}"'  # 证书序列号部分
    )
    return authorization  # 返回构建的授权头
