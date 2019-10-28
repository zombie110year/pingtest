from pingtest.ping import MicrosoftPing


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
