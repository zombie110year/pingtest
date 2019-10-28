"""Ping 命令
"""
import re
import socket
from os import remove
from subprocess import PIPE
from subprocess import run
from time import perf_counter
from typing import Iterable

from .icmp import ICMPConnect
from .icmp import ICMPMessage

# PingReport = namedtuple("PingReport", ("dest", "status", "cost_time"))


class PingReport(dict):
    """关于 Ping 测试的简单报告

    :attr addr: str, 目标地址
    :attr loss: 0~1, float, 丢包率
    :attr mint: float, ms, 最小时延
    :attr maxt: float, ms, 最大时延
    :attr avgt: float, ms, 平均时延

    :attr ipv: 4|6, IP 版本
    :attr count: int, 发包数量
    :attr size: int, 字节, 发包大小
    """
    def __init__(self, addr: str, loss:float, mint: float, maxt:float, avgt:float,**kwargs):
        self["addr"] = addr
        self["loss"] = loss
        self["mint"] = mint
        self["maxt"] = maxt
        self["avgt"] = avgt
        self.update(kwargs)


def ping_once(target: str, data: bytes) -> PingReport:
    m = ICMPMessage(data)
    ic = ICMPConnect(target)
    start = perf_counter()
    ic.send(m)
    try:
        reply, address = ic.recv()
        status = "reached"
    except socket.timeout:
        status = "timeout"
        address = (target, -1)
    stop = perf_counter()
    report = PingReport(address[0], status, stop-start)
    return report


def ping(target: str, data: bytes, count=4) -> Iterable[PingReport]:
    m = ICMPMessage(data)
    ic = ICMPConnect(target)
    reports = []
    for i in range(count):
        ic.send(m)
        start = perf_counter()
        try:
            reply, address = ic.recv()
            status = "reach"
            m.seq += 1
        except socket.timeout:
            status = "timeout"
            address = (target, -1)
        stop = perf_counter()
        report = PingReport(address[0], status, stop-start)
        reports.append(report)
    return reports


class MicrosoftPing:
    """微软 ping 程序

    通过解析 stdout 获得数据。

    构造时通过参数创建对应的外部程序调用：

    >>> str(MicrosoftPing("localhost"))
    ping.exe localhost
    >>> str(MicrosoftPing("localhost", count=4, size=32))
    ping.exe -n 4 -l 32 localhost

    构造后，调用 run 方法获取返回结果

    >>> ping = MicrosoftPing("localhost")
    >>> ping.run()
    """
    REGEX = re.compile(r"(?:(\d+)%)|(?:(\d+)ms)", re.MULTILINE)
    def __init__(self, addr: str, **options):
        """初始化 Ping 进程与解析器

        :param str addr: 要 ping 的目标地址
        :param int count: 发包的次数
        :param int size: 每个包的字节数
        :param bool ipv4:
        """
        self.exec = "ping.exe"
        self.target = f"{addr}"
        self.args = []
        self.options = dict()

        if "ipv4" in options.keys() and "ipv6" not in options.keys():
            self.args.append("-4")
            self.options["ipv"] = 4
        elif "ipv6" in options.keys() and "ipv4" not in options.keys():
            self.args.append("-6")
            self.options["ipv"] = 6
        elif "ipv6" not in options.keys() and "ipv6" not in options.keys():
            pass
        else:
            raise ValueError(f"ipv4 或 ipv6 不能同时存在")

        if count := options.get("count", None):
            self.args.append("-n")
            self.args.append(f"{count}")
            self.options["count"] = int(count)

        if size := options.get("size", None):
            self.args.append("-l")
            self.args.append(f"{size}")
            self.options["size"] = int(size)

    @property
    def command(self):
        return [self.exec] + self.args + [self.target]


    def run(self) -> PingReport:
        cmp = run(self.command, shell=False, stdout=PIPE, encoding=get_system_encoding())
        res = cmp.stdout

        return self._parse_stdout(res)

    def _parse_stdout(self, text: str) -> PingReport:
        lines = text.split("\n")[-3:]
        summary = "\n".join(lines)
        data = self.REGEX.findall(summary)
        report = PingReport(
            self.target, data[0], data[1], data[2], data[3],
            **self.options
        )
        return report

    def __str__(self):
        return f"{self.exec} {' '.join(self.args)} {self.target}"

__system_encoding = None
def get_system_encoding():
    """获取当前操作系统的字符编码，用于 Windows，会创建一个临时文件

    不要与 Python 的字符串默认编码混淆了，这个编码是操作系统 stdio 的默认编码
    """
    global __system_encoding
    if __system_encoding:
        return __system_encoding
    else:
        temp_filename = "no-one-will-call-this-name.no-one-will-call-this-name"
        with open(temp_filename, "wt") as temporary:
            encoding = temporary.encoding
        remove(temp_filename)
        __system_encoding = encoding
        return encoding
