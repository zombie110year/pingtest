from pingtest.ping import MicrosoftPing
from pingtest.ping import GNUPing


def test_parse_ping_stdout_ms():
    text = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=41ms TTL=45
Reply from 8.8.8.8: bytes=32 time=42ms TTL=45
Reply from 8.8.8.8: bytes=32 time=42ms TTL=45
Request timed out.

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),
Approximate round trip times in milli-seconds:
    Minimum = 41ms, Maximum = 42ms, Average = 41ms
"""
    a = MicrosoftPing("8.8.8.8")
    res = a._parse_stdout(text)
    assert res["addr"] == "8.8.8.8"
    assert res["loss"] == 0.25
    assert res["mint"] == 41.0
    assert res["maxt"] == 42.0
    assert res["avgt"] == 41.0


def test_parse_ping_stdout_gnu():
    text = """
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=45 time=39.9 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=45 time=40.8 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=45 time=40.8 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=45 time=40.2 ms
64 bytes from 8.8.8.8: icmp_seq=5 ttl=45 time=40.2 ms
64 bytes from 8.8.8.8: icmp_seq=6 ttl=45 time=40.2 ms
64 bytes from 8.8.8.8: icmp_seq=7 ttl=45 time=39.5 ms
64 bytes from 8.8.8.8: icmp_seq=8 ttl=45 time=40.2 ms
64 bytes from 8.8.8.8: icmp_seq=10 ttl=45 time=42.3 ms
64 bytes from 8.8.8.8: icmp_seq=11 ttl=45 time=40.1 ms
64 bytes from 8.8.8.8: icmp_seq=14 ttl=45 time=39.6 ms
64 bytes from 8.8.8.8: icmp_seq=19 ttl=45 time=42.7 ms
64 bytes from 8.8.8.8: icmp_seq=20 ttl=45 time=41.3 ms
64 bytes from 8.8.8.8: icmp_seq=22 ttl=45 time=39.9 ms
64 bytes from 8.8.8.8: icmp_seq=23 ttl=45 time=41.1 ms
64 bytes from 8.8.8.8: icmp_seq=24 ttl=45 time=43.4 ms

--- 8.8.8.8 ping statistics ---
24 packets transmitted, 16 received, 33.3333% packet loss, time 43ms
rtt min/avg/max/mdev = 39.548/40.770/43.370/1.115 ms
"""
    a = GNUPing("8.8.8.8")
    assert a.options["count"] == 4

    res = a._parse_stdout(text)
    assert res["loss"] == 0.333333
    assert res["mint"] == 39.548
    assert res["avgt"] == 40.770
    assert res["maxt"] == 43.370
