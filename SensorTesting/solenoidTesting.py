import machine
import time

solenoid2A = machine.Pin(20, machine.Pin.OUT)
solenoid2B = machine.Pin(21, machine.Pin.OUT)

while True:
    #solenoid2A.value(True)
    #solenoid2B.value(False)
    #print("Extend")
    #time.sleep(2)
    
    solenoid2A.value(False)
    solenoid2B.value(True)
    print("Retract")
    time.sleep(2)
    
    solenoid2A.value(False)
    solenoid2B.value(False)
    print("Loose")
    time.sleep(2)