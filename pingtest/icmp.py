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

__all__ = ("ICMPMessage", "ICMPConnect")


def icmp_checksum(content: bytes) -> int:
    """计算 icmp 报文的检验和。

    计算的范围为整个 icmp 报文，包括头部与数据部。
    每次取两个字节，累加（溢出部分被截断），输出最后的和。
    """
    length = len(content)
    if length & 1:  # 奇数
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
    return (~result) & 0xffff


class ICMPMessage:
    """一个 ICMP 报文

    - 8 bit Type
    - 8 bit code
    - 16 bit checksum
    - 16 bit ID
    - 16 bit sequence
    - ... content
    """
    __slots__ = ("type", "code", "__checksum_cache",
                 "id", "seq", "data", "length")
    TYPE_ECHO_REQUEST = 8

    @property
    def ICMP_STRUCT(self):
        return f">BBHHH{self.length}s"

    def pack(self):
        """序列化此对象，打包成结构体以便发送
        """
        return struct.pack(self.ICMP_STRUCT,
                           self.type, self.code, self.checksum, self.id, self.seq, self.data)

    def __init__(self, data: bytes, type: int = 8, code: int = 0, id: int = 0, seq: int = 0):
        if not isinstance(data, bytes):
            raise TypeError("data: must bytes", data)
        self.type = type
        self.code = code
        self.id = id
        self.seq = seq
        self.data = data
        self.length = len(data)
        self.__checksum_cache = None

    @property
    def checksum(self) -> int:
        """ICMP 报文的检验和, unsigned short
        """
        if self.__checksum_cache is None:
            # 将检验和置零
            all_content = struct.pack(self.ICMP_STRUCT,
                                      self.type, self.code, 0, self.id, self.seq, self.data)
            self.__checksum_cache = icmp_checksum(all_content)
        return self.__checksum_cache


class ICMPConnect:
    """一个 ICMP 连接
    """

    def recv(self, size=1024, timeout=3):
        return self.s.recvfrom(size)

    def send(self, message: ICMPMessage):
        packet = message.pack()
        self.s.sendto(packet, (self.target, self.port))

    def __init__(self, target: str, port=80):
        self.target = target
        self.port = port
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
