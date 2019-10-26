from pingtest.icmp import ICMPMessage


def test_icmp_checksum():
    "偶数长度"
    assert ICMPMessage(b"").checksum == 0xf7ff
    assert ICMPMessage(b"ab").checksum == 0x969d
    assert ICMPMessage(b"abcd").checksum == 0x3339
    assert ICMPMessage(b"abcdef").checksum == 0xcdd2
    assert ICMPMessage(b"abcdefgh").checksum == 0x666a
    assert ICMPMessage(b"abcdefghij").checksum == 0xfcff
    assert ICMPMessage(b"abcdefghijkl").checksum == 0x9193
    assert ICMPMessage(b"abcdefghijklmn").checksum == 0x2425
    assert ICMPMessage(b"abcdefghijklmnop").checksum == 0xb4b4
    assert ICMPMessage(b"abcdefghijklmnopqr").checksum == 0x4342
    assert ICMPMessage(b"abcdefghijklmnopqrst").checksum == 0xcfcd
    assert ICMPMessage(b"abcdefghijklmnopqrstuv").checksum == 0x5a57
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwx").checksum == 0xe2de
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz").checksum == 0x6964
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz12").checksum == 0x3832
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz1234").checksum == 0x04fe
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz123456").checksum == 0xcfc7

def test_icmp_checksum2():
    "奇数长度"
    assert ICMPMessage(b"a").checksum == 0x96ff
    assert ICMPMessage(b"abc").checksum == 0x339d
    # delta + 1
    assert ICMPMessage(b"abcde").checksum == 0xce38
    assert ICMPMessage(b"abcdefg").checksum == 0x66d2
    # delta + 1
    assert ICMPMessage(b"abcdefghi").checksum == 0xfd69
    assert ICMPMessage(b"abcdefghijk").checksum == 0x91ff
    assert ICMPMessage(b"abcdefghijklm").checksum == 0x2493
    # delta + 1
    assert ICMPMessage(b"abcdefghijklmno").checksum == 0xb524
    assert ICMPMessage(b"abcdefghijklmnopq").checksum == 0x43b4
    # delta + 1
    assert ICMPMessage(b"abcdefghijklmnopqrs").checksum == 0xd041
    assert ICMPMessage(b"abcdefghijklmnopqrstu").checksum == 0x5acd
    # delta + 1
    assert ICMPMessage(b"abcdefghijklmnopqrstuvw").checksum == 0xe356
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxy").checksum == 0x69de
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz1").checksum == 0x3864
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz123").checksum == 0x0532
    assert ICMPMessage(b"abcdefghijklmnopqrstuvwxyz12345").checksum == 0xcffd
