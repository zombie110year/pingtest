import struct


class BOBytes:
    """可进行位运算的字节
    """

    def __init__(self, data):
        if isinstance(data, bytes):
            self.data = data
        elif isinstance(data, BOBytes):
            self = data
        else:
            raise TypeError(f"{data} is not bytes.")

    def __repr__(self):
        return self.data

    def __len__(self):
        return self.data.__len__()

    def __iter__(self):
        self.__iter_ind = 0
        return self

    def __next__(self):
        if self.__iter_ind < len(self):
            self.__iter_ind += 1
            return self.data[self.__iter_ind - 1]
        else:
            raise StopIteration

    def __getitem__(self, index) -> bytes:
        return self.data[index]

    def __and__(self, other):
        if not isinstance(other, (bytes, BOBytes)):
            raise TypeError(f"{other} is not bytes.")
        if len(other) != len(self.data):
            raise ValueError(f"length of {other} is not equal to {self.data}")

        result = (
            struct.pack("B",
                        struct.unpack("B", a) & struct.unpack("B", b)
                        ) for a, b in zip(self.data, other)
        )

        return b"".join(result)
