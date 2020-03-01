import functools
import itertools
import operator

from . import packets


class Motor:

    def __init__(self, cxn, id_):
        self.cxn = cxn
        self.rom = Rom(cxn, id_)

    def restart(self):
        packet = packets.SpecialCommandPacket(
            self.id, flag=0x20, address=0xff, length=0x00)
        self.cxn.command(packet)

    def factory_reset(self):
        packet = packets.SpecialCommandPacket(
            self.id, flag=0x10, address=0xff, length=0xff)
        self.cxn.command(packet)

    @property
    def model_no(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x00, length=2)
        return self.cxn.query(packet).data[::-1]  # h, l

    @property
    def firm_version(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x02)
        return self.cxn.query(packet).data

    @property
    def id(self):
        return self.rom.id

    @id.setter
    def id(self, new_id):
        self.rom.id = new_id

    def rotate(self, degree, msec=None):
        check_limit(degree, -150.0, 150.0)
        if msec is None:
            msec = 0
        check_limit(msec, 0, 163830)
        data = degree_to_data(degree) + msec_to_data(msec)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x1e, data=data)
        self.cxn.command(packet)

    @property
    def max_torque(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x23)
        return ord(self.cxn.query(packet).data)  # percent

    @max_torque.setter
    def max_torque(self, percent):
        check_limit(percent, 0, 100)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x23, data=[percent])
        self.cxn.command(packet)

    @property
    def torque_mode(self):
        map_ = {0x00: 'off', 0x01: 'on', 0x02: 'brake'}
        packet = packets.SingleDataQueryPacket(self.id, address=0x24)
        return map_[ord(self.cxn.query(packet).data)]

    @torque_mode.setter
    def torque_mode(self, mode):
        map_ = {'off': 0x00, 'on': 0x01, 'brake': 0x02}
        check_key(mode, map_.keys())
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x24, data=[map_[mode]])
        self.cxn.command(packet)

    @property
    def torque_enabled(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x24)
        if ord(self.cxn.query(packet).data) == 0:
            return False
        else:
            return True  # 1 or 2

    @torque_enabled.setter
    def torque_enabled(self, enabled):
        if enabled:
            self.torque_mode = 'on'
        else:
            self.torque_mode = 'off'

    @property
    def pid_coeff(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x26)
        return ord(self.cxn.query(packet).data)  # percent

    @pid_coeff.setter
    def pid_coeff(self, percent):
        check_limit(percent, 1, 255)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x26, data=[percent])
        self.cxn.command(packet)

    @property
    def angle(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_degree(self.cxn.query(packet).data[0:2])  # degree

    @angle.setter
    def angle(self, degree):
        self.rotate(degree)

    @property
    def time(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_value(self.cxn.query(packet).data[2:4]) * 10  # ms

    @property
    def speed(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_value(self.cxn.query(packet).data[4:6])  # deg/sec

    @property
    def load(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_value(self.cxn.query(packet).data[6:8])  # mA

    @property
    def temperature(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_value(self.cxn.query(packet).data[8:10])  # Celsius

    @property
    def voltage(self):
        packet = packets.MultiDataQueryPacket(self.id, flag=0x09)
        return data_to_volt(self.cxn.query(packet).data[10:12])  # V


class Rom:

    def __init__(self, cxn, id_):
        self.cxn = cxn
        self._id = id_

    def write(self):
        packet = packets.SpecialCommandPacket(
            self.id, flag=0x40, address=0xff, length=0x00)
        self.cxn.command(packet)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        check_limit(new_id, 1, 127)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x04, data=[new_id])
        self.cxn.command(packet)
        self._id = new_id

    @property
    def reversed(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x05)
        if ord(self.cxn.query(packet).data) == 0:
            return False
        else:
            return True  # 1

    @reversed.setter
    def reversed(self, reversed):
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x05, data=[0x01 if reversed else 0x00])
        self.cxn.command(packet)

    @property
    def baudrate(self):
        map_ = {
            0x00: 9600,
            0x01: 14400,
            0x02: 19200,
            0x03: 28800,
            0x04: 38400,
            0x05: 57600,
            0x06: 76800,
            0x07: 115200,
            0x08: 153600,
            0x09: 230400
        }
        packet = packets.SingleDataQueryPacket(self.id, address=0x06)
        return map_[ord(self.cxn.query(packet).data)]

    @baudrate.setter
    def baudrate(self, bps):
        map_ = {
            9600: 0x00,
            14400: 0x01,
            19200: 0x02,
            28800: 0x03,
            38400: 0x04,
            57600: 0x05,
            76800: 0x06,
            115200: 0x07,
            153600: 0x08,
            230400: 0x09
        }
        check_key(bps, map_.keys())
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x06, data=[map_[bps]])
        self.cxn.command(packet)

    @property
    def return_delay(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x07)
        return (ord(self.cxn.query(packet).data) * 50) + 100  # us

    @return_delay.setter
    def return_delay(self, us):
        check_limit(us, 100, 12850)  # limit is undocumented
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x07, data=[(us - 100) // 50])
        self.cxn.command(packet)

    @property
    def cw_angle_limit(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x08, length=2)
        return data_to_degree(self.cxn.query(packet).data)  # degree

    @cw_angle_limit.setter
    def cw_angle_limit(self, degree):
        check_limit(degree, 0, 150.0)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x08, data=degree_to_data(degree))
        self.cxn.command(packet)

    @property
    def ccw_angle_limit(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x0a, length=2)
        return data_to_degree(self.cxn.query(packet).data)  # degree

    @ccw_angle_limit.setter
    def ccw_angle_limit(self, degree):
        check_limit(degree, -150.0, 0)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x0a, data=degree_to_data(degree))
        self.cxn.command(packet)

    @property
    def temperature_limit(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x0e, length=2)
        return data_to_value(self.cxn.query(packet).data)  # Celsius

    @property
    def torque_in_silence(self):
        map_ = {0x00: 'off', 0x01: 'on', 0x02: 'brake'}
        packet = packets.SingleDataQueryPacket(self.id, address=0x16)
        return map_[ord(self.cxn.query(packet).data)]

    @torque_in_silence.setter
    def torque_in_silence(self, mode):
        map_ = {'off': 0x00, 'on': 0x01, 'brake': 0x02}
        check_key(mode, map_.keys())
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x16, data=[map_[mode]])
        self.cxn.command(packet)

    @property
    def warmup_time(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x17)
        return ord(self.cxn.query(packet).data) * 10  # ms

    @warmup_time.setter
    def warmup_time(self, ms):
        check_limit(ms, 0, 2550)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x17, data=[(ms // 10)])
        self.cxn.command(packet)

    @property
    def cw_compliance_margin(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x18)
        return ord(self.cxn.query(packet).data) / 10  # degree

    @cw_compliance_margin.setter
    def cw_compliance_margin(self, degree):
        check_limit(degree, 0, 25.5)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x18, data=[int(degree * 10)])
        self.cxn.command(packet)

    @property
    def ccw_compliance_margin(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x19)
        return ord(self.cxn.query(packet).data) / 10  # degree

    @ccw_compliance_margin.setter
    def ccw_compliance_margin(self, degree):
        check_limit(degree, 0, 25.5)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x19, data=[int(degree * 10)])
        self.cxn.command(packet)

    @property
    def cw_compliance_slope(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x1a)
        return ord(self.cxn.query(packet).data)  # degree

    @cw_compliance_slope.setter
    def cw_compliance_slope(self, degree):
        check_limit(degree, 0, 255)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x1a, data=[degree])
        self.cxn.command(packet)

    @property
    def ccw_compliance_slope(self):
        packet = packets.SingleDataQueryPacket(self.id, address=0x1b)
        return ord(self.cxn.query(packet).data)  # degree

    @ccw_compliance_slope.setter
    def ccw_compliance_slope(self, degree):
        check_limit(degree, 0, 255)
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x1b, data=[degree])
        self.cxn.command(packet)

    @property
    def punch(self):
        # It uses raw bytes
        # because the punch value is different depending on the motor model.
        packet = packets.SingleDataQueryPacket(self.id, address=0x1c, length=2)
        return self.cxn.query(packet).data[::-1]  # h, l

    @punch.setter
    def punch(self, data):  # data = [h, l]
        # It uses raw bytes
        # because the punch value is different depending on the motor model.
        packet = packets.SingleDataCommandPacket(
            self.id, address=0x1c, data=data[::-1])
        self.cxn.command(packet)


class MotorList(list):

    @property
    def torque_modes(self):
        return [m.torque_mode for m in self]

    @torque_modes.setter
    def torque_modes(self, modes):
        map_ = {'off': 0x00, 'on': 0x01, 'brake': 0x02}
        for m in modes:
            check_key(m, map_.keys())
        data = itertools.chain.from_iterable(
            zip([m.id for m in self], [map_[m] for m in modes]))
        packet = packets.MultiDataCommandPacket(
            address=0x24,
            length=0x02,
            count=len(self),
            data=data
        )
        self[0].cxn.command(packet)

    @property
    def torque_enabled(self):
        return [m.torque_enabled for m in self]

    @torque_enabled.setter
    def torque_enabled(self, enabled):
        self.torque_modes = (['on'] if enabled else ['off']) * len(self)

    def rotate(self, degrees, msecs=None):
        for d in degrees:
            check_limit(d, -150.0, 150.0)
        zippee = [
            [bytes([m.id]) for m in self],
            [degree_to_data(d) for d in degrees]
        ]
        if msecs is not None:
            for s in msecs:
                check_limit(s, 0, 163830)
            zippee.append([msec_to_data(s) for s in msecs])
        data = itertools.chain.from_iterable(
            [functools.reduce(operator.add, e) for e in zip(*zippee)])
        packet = packets.MultiDataCommandPacket(
            address=0x1e,
            length=0x03 if msecs is None else 0x05,
            count=len(self),
            data=data
        )
        self[0].cxn.command(packet)

    @property
    def angles(self):
        return [m.angle for m in self]

    @angles.setter
    def angles(self, degrees):
        self.rotate(degrees)


def degree_to_data(degree):
    return value_to_data(int(degree * 10))


def msec_to_data(msec):
    return value_to_data(msec // 10)


def value_to_data(v):
    return v.to_bytes(2, 'little', signed=True)


def data_to_degree(data):
    return data_to_value(data) / 10


def data_to_volt(data):
    return data_to_value(data) / 100


def data_to_value(data):
    return int.from_bytes(data, 'little', signed=True)


def check_limit(value, lower, upper):
    if not (lower <= value <= upper):
        raise ValueError(f'value must be between {lower} and {upper}')


def check_key(value, keys):
    if value not in keys:
        raise ValueError(f'value must be one of {keys}')
