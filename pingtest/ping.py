"""Ping 命令
"""
import re
import socket
from os import remove
from platform import system
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
    REGEX = re.compile(r"(\d+)(?:(?=%)|(?=ms))", re.MULTILINE)
    def __init__(self, addr: str, **options):
        """初始化 Ping 进程与解析器

        :param str addr: 要 ping 的目标地址
        :param int count: 发包的次数
        :param int size: 每个包的字节数
        :param bool ipv4: 是否限制只能使用 ipv4
        :param bool ipv6: 是否限制只能使用 ipv6
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
        cmp = run(self.command, shell=False, stdout=PIPE, text=True)
        res = cmp.stdout

        return self._parse_stdout(res)

    def _parse_stdout(self, text: str) -> PingReport:
        lines = text.split("\n")[-4:]
        summary = "\n".join(lines)
        data = self.REGEX.findall(summary)
        loss = float(data[0]) / 100
        mint = float(data[1])
        maxt = float(data[2])
        avgt = float(data[3])
        report = PingReport(
            self.target, loss, mint, maxt, avgt,
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
    DeprecationWarning("将被移除")
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


class GNUPing:
    """GNU utils 中的 ping 程序

    通过解析 stdout 获得数据。

    构造时通过参数创建对应的外部程序调用：

    >>> str(GNUPing("localhost"))
    ping localhost
    >>> str(GNUPing("localhost", count=4, size=32))
    ping -c 4 -l 32 localhost

    构造后，调用 run 方法获取返回结果

    >>> ping = GNUPing("localhost")
    >>> ping.run()
    """
    REGEX1 = re.compile(r"(\d+(?:.\d+)?)(?=%)")
    REGEX2 = re.compile(r"(\d+(?:.\d+)?)/(\d+(?:.\d+)?)/(\d+(?:.\d+)?)/\d+(?:.\d+)? ms")
    def __init__(self, addr: str, **options):
        """初始化 Ping 进程与解析器

        :param str addr: 要 ping 的目标地址
        :param int count: 发包的次数
        :param int size: 每个包的字节数
        :param bool ipv4: 是否限制只能使用 ipv4
        :param bool ipv6: 是否限制只能使用 ipv6
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

        if count := options.get("count", 4):
            self.args.append("-c")
            self.args.append(f"{count}")
            self.options["count"] = int(count)

        if size := options.get("size", None):
            self.args.append("-s")
            self.args.append(f"{size}")
            self.options["size"] = int(size)

    @property
    def command(self):
        return [self.exec] + self.args + [self.target]


    def run(self) -> PingReport:
        cmp = run(self.command, shell=False, stdout=PIPE, text=True)
        res = cmp.stdout

        return self._parse_stdout(res)


    def _parse_stdout(self, text: str) -> PingReport:
        summary1 = text.split("\n")[-3] # loss
        summary2 = text.split("\n")[-2] # min/avg/max
        loss = float(self.REGEX1.search(summary1)[1]) / 100
        tgroup = self.REGEX2.search(summary2)
        mint = float(tgroup[1])
        avgt = float(tgroup[2])
        maxt = float(tgroup[3])
        report = PingReport(
            self.target, loss, mint, maxt, avgt,
            **self.options
        )
        return report

    def __str__(self):
        return f"{self.exec} {' '.join(self.args)} {self.target}"


def Ping(addr, **options):
    """初始化 Ping 进程与解析器

    :param str addr: 要 ping 的目标地址
    :param int count: 发包的次数
    :param int size: 每个包的字节数
    :param bool ipv4: 是否限制只能使用 ipv4
    :param bool ipv6: 是否限制只能使用 ipv6
    """
    if system() == "Windows":
        return MicrosoftPing(addr, **options)
    elif system() == "Linux":
        return GNUPing(addr, **options)
    else:
        Warning("不知道你使用的 ping 为哪种版本，姑且认为是 GNU 版，如果出错，请 issue 你的系统名以及 ping 版本")
        return GNUPing(addr, **options)
