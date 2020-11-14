# dicot

Controls Futaba Command-Type Servo motors. It is developed and tested with [RS204MD](http://www.futaba.co.jp/robot/command_type_servos/rs204md).

## Installation

```shell
$ pip install dicot
```

## Usage

Create the serial port connection, enable the torque, and set the motor angle:

```pycon
>>> import dicot
>>>
>>> cnx = dicot.open('COM1')
>>>
>>> motor = cnx.motor(1)  # id = 1
>>> motor.torque_enabled = True
>>>
>>> motor.angle = 45  # degree
```

Or set with duration:

```pycon
>>> motor.rotate(90, msec=5000)  # with duration
```

Can get and set various parameters through the attributes:

```pycon
>>> motor.angle
90  # degree
>>>
>>> motor.load
6  # mA
>>>
>>> motor.temperature
30  # Celsius
>>>
>>> motor.voltage
5.2  # V
>>>
>>> motor.max_torque = 80  # %
>>> motor.pid_coeff = 100  # %
```

The value set in the ROM area must be written by executing `motor.rom.write()` in order to retain it even after the motor is turned off:

```pycon
>>> motor.torque_enabled = False
>>> motor.rom.cw_angle_limit = 100  # degree
>>> motor.rom.ccw_compliance_margin = 0.2  # degree
>>> motor.rom.ccw_compliance_slope = 20  # degree
>>> motor.rom.write()
```

Can also change the ID:

```pycon
>>> motor.rom.id = 2
>>> motor.rom.write()
```

MotorList can handle multiple motors collectively:

```pycon
>>> motors = dicot.MotorList([motor, cnx.motor(2), cnx.motor(3)])
>>> motors.torque_enabled = True
>>> motors.angles = [30, 60, 90]
```

The connection object supports the with statement:

```python  
import dicot

with dicot.open('COM1') as cnx:
    motor = cnx.motor(1)
    print(motor.firm_version)
```  
