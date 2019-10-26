from pingtest.icmp import ICMPMessage

def test_icmp_checksum():
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz123456").checksum == 0xcfc7
    assert ICMPMessage(b"").checksum == 0xf7ff
    assert ICMPMessage(b"\x00\x00\x00\x00").checksum == 0xf7ff
    assert ICMPMessage(b"\x00\x01\x02").checksum == 0xf5fe
