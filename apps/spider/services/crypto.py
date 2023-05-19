# -- coding: utf-8 --
# @Time : 2023/5/18 16:32
# @Author : zhuo.wang
# @File : crypto.py

from base64 import b64decode
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
from Crypto.Util.py3compat import b

def decrypt(ciphertext):
    key = b("1qaz@wsx")
    cipher = DES.new(key, DES.MODE_ECB)

    # 需要注意，JavaScript代码中输入的是一个Base64编码的字符串
    decoded = b64decode(ciphertext)
    decrypted = unpad(cipher.decrypt(decoded), DES.block_size)

    return decrypted.decode('utf-8')
