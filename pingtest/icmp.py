"""网络相关

ICMP 协议
=========

ICMP 协议包的发送与接收使用 ICMPConnect 类实现。
ICMP 报文定义为 ICMPMessage 类。

HTTP 协议
=========
"""
import struct
import socket



def icmp_checksum(content: bytes) -> int:
    """计算 icmp 报文的检验和。

    计算的范围为整个 icmp 报文，包括头部与数据部。
    每次取两个字节，累加（溢出部分被截断），输出最后的和。
    """
    length = len(content)
    if length & 1: # 奇数
        content += b"\x00"
        length += 1
    # 确保按两个字节的步长取值
    steps = length // 2
    result = 0
    for i in range(steps):
        fragment = content[2*i:2*i+2]
        # 按两个字节累加
        this = int.from_bytes(fragment, "big")
        result += this
        # 截断溢出部分
        result &= 0xffff
    return result
