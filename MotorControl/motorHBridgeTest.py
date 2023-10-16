import machine
import time

# Motor 1
in1 = machine.Pin(10, machine.Pin.OUT)
in2 = machine.Pin(11, machine.Pin.OUT)

# Motor 2
in3 = machine.Pin(12, machine.Pin.OUT)
in4 = machine.Pin(13, machine.Pin.OUT)

#
"""
TODO: Add in PWM Control
(which begs how do we want the operator to control?)
"""

# Rotate CW for 1s, stop, then rotate CCW, stop, repeat
while True:
    print("->")
    in1.value(1)
    in2.value(0)
    time.sleep(1)
    
    in1.value(0)
    in2.value(0)
    time.sleep(1)
    
    print("<-")
    in2.value(1)
    in1.value(0)
    time.sleep(1)
    
    in1.value(0)
    in2.value(0)
    time.sleep(1)
