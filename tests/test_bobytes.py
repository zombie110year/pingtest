from pingtest.bobytes import BOBytes


def test_iterable():
    "BOBytes 应当可以被迭代"
    results = b"123456789"
    for i, b in enumerate(BOBytes(results)):
        b == results[i]


def test_getitem():
    "BOBytes 应当可以被索引"
    assert BOBytes(b"123")[1:2] == b"2"
    assert BOBytes(b"123")[:] == b"123"
