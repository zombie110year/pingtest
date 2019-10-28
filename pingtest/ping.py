"""Ping 命令
"""
import socket
from time import perf_counter
from typing import Iterable

from .icmp import ICMPConnect
from .icmp import ICMPMessage

# PingReport = namedtuple("PingReport", ("dest", "status", "cost_time"))


class PingReport(dict):
    def __init__(self, dest: str, status: str, cost_time: float):
        super().__init__(dest=dest, status=status, cost_time=cost_time)


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
