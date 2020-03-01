import serial

from . import motors
from . import packets


def open(port, baudrate=115200, timeout=1):
    cnx = Connection(port, baudrate, timeout)
    cnx.open()
    return cnx


class Connection:

    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = timeout

    def open(self):
        self.ser.open()

    def close(self):
        self.ser.close()

    def motor(self, id_):
        return motors.Motor(self, id_)

    def command(self, packet):
        self.ser.write(packet.bytes)

    def query(self, packet):
        self.ser.write(packet.bytes)
        return packets.ReturnPacket(self.ser.read(packet.query_length))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
