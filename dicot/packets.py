class WrapperPacket:

    @property
    def bytes(self):
        return self.content.bytes


class SingleDataCommandPacket(WrapperPacket):

    def __init__(self, id_, address, length=None, data=None):
        if data is None:
            data = []
        self.content = ShortPacket(
            id_=id_,
            flag=0x00,
            address=address,
            length=len(data) if length is None else length,
            count=0x01,
            data=data
        )


class MultiDataCommandPacket(WrapperPacket):

    def __init__(self, address, length, count, data):
        self.content = LongPacket(
            address=address,
            length=length,
            count=count,
            data=data
        )


class SpecialCommandPacket(WrapperPacket):

    def __init__(self, id_, flag, address, length):
        self.content = ShortPacket(
            id_=id_,
            flag=flag,
            address=address,
            length=length,
            count=0x00,
            data=[]
        )


class SingleDataQueryPacket(WrapperPacket):

    def __init__(self, id_, address, length=1):
        self.content = ShortPacket(
            id_=id_,
            flag=0x0f,
            address=address,
            length=length,
            count=0x00,
            data=[]
        )
        self.query_length = length + 8


class MultiDataQueryPacket(WrapperPacket):

    def __init__(self, id_, flag):
        length_map = {
            0x03: 30,  # no. 00-29
            0x05: 30,  # no. 30-59
            0x07: 10,  # no. 20-29
            0x09: 18,  # no. 42-59
            0x0b: 12,  # no. 30-41
            0x0d: 67  # no. 60-127
        }
        self.content = ShortPacket(
            id_=id_,
            flag=flag,
            address=0x00,
            length=0x00,
            count=0x01,
            data=[]
        )
        self.query_length = length_map[flag] + 8


class ShortPacket:

    def __init__(self, id_, flag, address, length, count, data):
        self.bytes = bytearray([
            0xfa, 0xaf,  # header
            id_,
            flag,
            address,
            length,
            count
        ])
        self.bytes.extend(data)
        self.bytes.append(checksum(self.bytes))


class LongPacket:

    def __init__(self, address, length, count, data):
        if data is None:
            data = []
        self.bytes = bytearray([
            0xfa, 0xaf,  # header
            0x00,  # id
            0x00,  # flag
            address,
            length,
            count
        ])
        self.bytes.extend(data)
        self.bytes.append(checksum(self.bytes))


class ReturnPacket:

    def __init__(self, bytes):
        self.bytes = bytes

    @property
    def data(self):
        return self.bytes[7:-1]


def checksum(bytes_):
    cs = bytes_[2]
    for b in bytes_[3:]:
        cs ^= b
    return cs
