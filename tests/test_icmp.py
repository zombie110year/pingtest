from pingtest.icmp import ICMPMessage
from pingtest.icmp import icmp_checksum

def test_icmp_checksum():
    assert icmp_checksum(b"\x08\x00" # type, code
                        b"\x00\x00" # checksum = 0
                        b"\x01\x00" # id
                        b"\x00\x00" # seq
                        # content
                        b"\x00\x00\x11\x22") == 0x1a22
    assert icmp_checksum(b"\x08\x00" # type, code
                        b"\x00\x00" # checksum = 0
                        b"\x01\x00" # id
                        b"\x00\x00" # seq
                        # content
                        b"\x00\x00\x11") == 0x1a00


def test_ICMPMessage_pack():
    x = ICMPMessage(b"Hello World", ICMPMessage.TYPE_ECHO_REQUEST)
    assert x.pack() == b"\x08\x00\x59\xcc\x00\x00\x00\x00Hello World"
