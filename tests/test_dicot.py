import pytest

import dicot


port = 'COM1'


@pytest.fixture
def cnx(mocker):
    mocker.patch('serial.Serial')
    return dicot.open(port)


class DummyPacket:

    def __init__(self, data_length):
        self.bytes = b'\x00' * (data_length + 8)


def test_connection(mocker):
    mocker.patch('serial.Serial')
    with dicot.open(port) as cnx:
        _ = cnx.motor(1)
    assert cnx.ser.port == port
    cnx.ser.open.assert_called_once()
    cnx.ser.close.assert_called_once()


def test_smoke(cnx):
    motor = cnx.motor(1)

    motor.rom.write()
    motor.restart()
    motor.factory_reset()

    cnx.ser.read.return_value = DummyPacket(2).bytes
    _ = motor.model_no
    cnx.ser.read.return_value = DummyPacket(1).bytes
    _ = motor.firm_version

    motor.id = 2
    motor.rom.id = 3
    motor.rom.reversed = True
    _ = motor.rom.reversed
    motor.rom.baudrate = 9600
    _ = motor.rom.baudrate
    motor.rom.return_delay = 200
    _ = motor.rom.return_delay
    cnx.ser.read.return_value = DummyPacket(2).bytes
    motor.rom.cw_angle_limit = 30.0
    _ = motor.rom.cw_angle_limit
    motor.rom.ccw_angle_limit = -120.0
    _ = motor.rom.ccw_angle_limit
    _ = motor.rom.temperature_limit
    cnx.ser.read.return_value = DummyPacket(1).bytes
    motor.rom.torque_in_silence = 'on'
    _ = motor.rom.torque_in_silence
    motor.rom.warmup_time = 1000
    _ = motor.rom.warmup_time
    motor.rom.cw_compliance_margin = 0.2
    _ = motor.rom.cw_compliance_margin
    motor.rom.ccw_compliance_margin = 0.1
    _ = motor.rom.ccw_compliance_margin
    motor.rom.cw_compliance_slope = 1
    _ = motor.rom.cw_compliance_slope
    motor.rom.ccw_compliance_slope = 2
    _ = motor.rom.ccw_compliance_slope
    cnx.ser.read.return_value = DummyPacket(2).bytes
    motor.rom.punch = [0x00, 0x08]
    _ = motor.rom.punch

    motor.rotate(45)
    motor.rotate(-60, 5000)
    cnx.ser.read.return_value = DummyPacket(1).bytes
    motor.max_torque = 100
    _ = motor.max_torque
    motor.torque_mode = 'on'
    motor.torque_mode = 'off'
    motor.torque_mode = 'brake'
    motor.torque_enabled = False
    motor.torque_enabled = True
    _ = motor.torque_mode
    _ = motor.torque_enabled
    motor.pid_coeff = 100
    _ = motor.pid_coeff
    cnx.ser.read.return_value = DummyPacket(18).bytes
    motor.angle = 90.0
    _ = motor.angle
    _ = motor.time
    _ = motor.speed
    _ = motor.load
    _ = motor.temperature
    _ = motor.voltage

    motors = dicot.MotorList([motor, cnx.motor(2), cnx.motor(3)])

    motors.rotate([30.0, 60.0, 90.0])
    motors.rotate([-30.0, -60.0, -90.0], [3000, 6000, 9000])
    motors.angles = [45.0, 0.0, -45.0]

    motors.torqu_modes = ['on', 'off', 'brake']
    motors.torque_enabled = True
    cnx.ser.read.return_value = DummyPacket(1).bytes
    _ = motors.torqu_modes
    _ = motors.torque_enabled

    cnx.ser.read.return_value = DummyPacket(18).bytes
    _ = motors.angles


def test_rom_write(cnx):
    motor = cnx.motor(1)
    motor.rom.write()
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x40\xff\x00\x00\xbe')


def test_restart(cnx):
    motor = cnx.motor(1)
    motor.restart()
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x20\xff\x00\x00\xde')


def test_factory_reset(cnx):
    motor = cnx.motor(1)
    motor.factory_reset()
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x10\xff\xff\x00\x11')


def test_change_id(cnx):
    motor = cnx.motor(1)
    motor.id = 5
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x04\x01\x01\x05\x00')


def test_reverse(cnx):
    motor = cnx.motor(1)
    motor.rom.reversed = True
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x05\x01\x01\x01\x05')


def test_baudrate(cnx):
    motor = cnx.motor(1)
    motor.rom.baudrate = 38400
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x06\x01\x01\x04\x03')


def test_return_delay(cnx):
    motor = cnx.motor(1)
    motor.rom.return_delay = 1000
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x07\x01\x01\x12\x14')


def test_cw_angle_limit(cnx):
    motor = cnx.motor(1)
    motor.rom.cw_angle_limit = 100
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x08\x02\x01\xe8\x03\xe1')


def test_ccw_angle_limit(cnx):
    motor = cnx.motor(1)
    motor.rom.ccw_angle_limit = -100
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x0a\x02\x01\x18\xfc\xec')


def test_punch(cnx):
    motor = cnx.motor(1)
    motor.rom.punch = [0x00, 0x64]
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x1c\x02\x01\x64\x00\x7a')


def test_rotate(cnx):
    motor = cnx.motor(1)
    motor.angle = 90
    motor.angle = -90
    cnx.ser.write.call_args_list == [
        b'\xfa\xaf\x01\x00\x1e\x02\x01\x84\x03\x9b',
        b'\xfa\xaf\x01\x00\x1e\x02\x01\x7c\xfc\x9c']


def test_rotate_with_duration(cnx):
    motor = cnx.motor(1)
    motor.rotate(90, 5000)
    motor.rotate(-120, 10000)
    cnx.ser.write.call_args_list == [
        b'\xfa\xaf\x01\x00\x1e\x04\x01\x84\x03\xf4\x01\x68',
        b'\xfa\xaf\x01\x00\x1e\x04\x01\x50\xfb\xe8\x03\x5a']


def test_max_torque(cnx):
    motor = cnx.motor(1)
    motor.max_torque = 80
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x23\x01\x01\x50\x72')


def test_torque_mode(cnx):
    motor = cnx.motor(1)
    motor.torque_enabled = True
    motor.torque_enabled = False
    motor.torque_mode = 'brake'
    cnx.ser.write.call_args_list == [
        b'\xfa\xaf\x01\x00\x24\x01\x01\x01\x24',
        b'\xfa\xaf\x01\x00\x24\x01\x01\x00\x25',
        b'\xfa\xaf\x01\x00\x24\x01\x01\x02\x27']


def test_pid_coeff(cnx):
    motor = cnx.motor(1)
    motor.pid_coeff = 90
    cnx.ser.write.assert_called_once_with(
        b'\xfa\xaf\x01\x00\x26\x01\x01\x5a\x7d')


def test_angle(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x84\x03\x00' \
        b'\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb9'
    motor = cnx.motor(1)
    angle = motor.angle
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert angle == 90


def test_time(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x5c\xff\x37' \
        b'\x02\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa9'
    motor = cnx.motor(1)
    time = motor.time
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert time == 5670


def test_speed(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x5c\xff\x37' \
        b'\x02\x2c\x01\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x84'
    motor = cnx.motor(1)
    speed = motor.speed
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert speed == 300


def test_load(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x4e\xfb\x00' \
        b'\x00\x00\x00\x06\x00\xba\x03\x00\x00\x00\x00\x00\x00\x00\x00\x32'
    motor = cnx.motor(1)
    load = motor.load
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert load == 6


def test_temperature(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x4e\xfb\x00' \
        b'\x00\x00\x00\x06\x00\x2d\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa6'
    motor = cnx.motor(1)
    temperature = motor.temperature
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert temperature == 45


def test_voltage(cnx):
    cnx.ser.read.return_value = b'\xfd\xdf\x01\x00\x2a\x12\x01\x4e\xfb\x00' \
        b'\x00\x00\x00\x06\x00\x2d\x00\xf4\x01\x00\x00\x00\x00\x00\x00\x53'
    motor = cnx.motor(1)
    voltage = motor.voltage
    cnx.ser.write.assert_called_once_with(b'\xfa\xaf\x01\x09\x00\x00\x01\x09')
    assert voltage == 5


def test_multiple_rotate(cnx):
    motors = dicot.MotorList([cnx.motor(1), cnx.motor(2), cnx.motor(5)])
    motors.angles = [10, 10, 50]
    b = b'\xfa\xaf\x00\x00\x1e\x03\x03\x01\x64\x00\x02\x64\x00\x05\xf4\x01\xed'
    cnx.ser.write.assert_called_once_with(b)
