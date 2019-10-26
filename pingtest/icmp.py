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
    如果数据长度不为偶数，需要在尾部填充一个 0 字节。
    创建一个 32 bit 的缓冲区，每次取两个字节（16 bit），累加。
    最后将前 16 bit 和后 16 bit 加在一起，取反，返回。
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
    high_bits = (result & 0xffff0000) >> 16
    low_bits = (result & 0xffff)
    ans = high_bits + low_bits
    return (~ans) & 0xffff


def extract_icmp_from_ip(packet: bytes) -> bytes:
    """从 IP 报文中提取出属于 imcp 报文的部分

    一个 ICMP 响应报文被包含在 IP 报文中，IP 报文头部结构为

    - 4 bit version
    - 4 bit head-length
    - 8 bit type-of-service
    - 16 bit all-length
    - 16 bit id
    - 3 bit flag
    - 13 bit offset
    - 8 bit ttl
    - 8 bit protocol
    - 16 bit checksum
    - 32 bit src-address
    - 32 bit dest-address
    - options ...
    """
    # icmp 报文外的 IP 头固定 20 字节
    head_length = 20
    return packet[head_length:]


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

    @staticmethod
    def unpack(packet: bytes):
        icmp_packet = extract_icmp_from_ip(packet)
        head = struct.unpack(">BBHHH", icmp_packet[:8])
        body = icmp_packet[8:]
        inst = ICMPMessage(body, head[0], head[1], head[3], head[4])
        return inst

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

    def __repr__(self):
        return (f"ICMPMessage({self.data}, type=0x{self.type:x}, "
                f"code=0x{self.code:x}, id=0x{self.id:x}, seq=0x{self.seq:x})\n"
                f"# checksum = 0x{self.checksum:x}")


class ICMPConnect:
    """一个 ICMP 连接

    建立一个 ICMP 连接:

    >>> ic = ICMPConnect("127.0.0.1")
    >>> ic
    ICMPConnect(target='127.0.0.1', port=80)

    发送一个 ICMPMessage:

    >>> # 先构造报文
    >>> m = ICMPMessage(b"Hello World")
    >>> # 发送
    >>> ic = ic.send(m)
    >>> # 需要立刻接收，否则丢包
    >>> message, address = ic.recv()
    >>> message
    ICMPMessage(b'Hello', type=0x0, code=0x0, id=0x0, seq=0x0)
    # checksum = 0xdc2d
    >>> address
    ('127.0.0.1', 0))
    """

    def recv(self, size=1024, timeout=3) -> tuple:
        """返回 ICMP 响应

        :return: 一个 ICMPMessage 实例和源地址
        """
        packet, address = self.s.recvfrom(size)
        icmp_message = ICMPMessage.unpack(packet)
        return icmp_message, address

    def send(self, message: ICMPMessage):
        packet = message.pack()
        self.s.sendto(packet, (self.target, self.port))

    def __init__(self, target: str, port=0):
        """初始化链接

        :param str target: 字符串类型的 IP 地址或域名
        :param int port: 发送到目标地址的指定端口，默认 0
        """
        self.target = target
        self.port = port
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))

    def __repr__(self):
        return f"ICMPConnect(target='{self.target}', port={self.port})"
