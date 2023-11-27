# Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
from hcsr04 import HCSR04
from time import sleep
import uasyncio as asyncio
import machine

# Serial Setup
serial = machine.UART(1, 115200)

# Distance Sensor Setup
sensor1 = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=10000)
sensor2 = HCSR04(trigger_pin=5, echo_pin=19, echo_timeout_us=10000)
sensor3 = HCSR04(trigger_pin=5, echo_pin=20, echo_timeout_us=10000)
sensor4 = HCSR04(trigger_pin=5, echo_pin=21, echo_timeout_us=10000)

# Motor Driver Setup
motorActivePin = machine.Pin(22, machine.Pin.OUT)

# State Setup
RUNNING = 0
STOPPED = 1

global state
state = RUNNING

# Coroutine Setup

async def motorRun():
    global state
    
    while True:
        print("Motor")
        
        print("State: " + str(state))
        motorActivePin.value(True)
            
        if(state == STOPPED):
            motorActivePin.value(False)
            
        await asyncio.sleep(0.1)

async def sensor1Check():
    global state
    
    while True:
        print("S1")
        currentDistance = sensor1.distance_cm()
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

async def sensor2Check():
    global state
    
    while True:
        print("S2")
        currentDistance = sensor2.distance_cm()
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

async def sensor3Check():
    global state
    
    while True:
        print("S3")
        currentDistance = sensor3.distance_cm()

        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING

        await asyncio.sleep(0.1)

async def sensor4Check():
    global state
    
    while True:
        print("S4")
        currentDistance = sensor4.distance_cm()
        print(str(currentDistance))
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

# Not Working
# async def taskSetup():
#     sensor1Task = asyncio.create_task(sensor1Check())
#     sensor2Task = asyncio.create_task(sensor2Check())
#     sensor3Task = asyncio.create_task(sensor3Check())
#     sensor4Task = asyncio.create_task(sensor4Check())
# 
#     motorTask = asyncio.create_task(motorRun())

# Main Setup
def main():
    try:
        # Get a permanently running event loop
        loop = asyncio.get_event_loop()

        sensor1Task = loop.create_task(sensor1Check())
        sensor2Task = loop.create_task(sensor2Check())
        sensor3Task = loop.create_task(sensor3Check())
        sensor4Task = loop.create_task(sensor4Check())

        motorTask = loop.create_task(motorRun())

        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        print("Stopped")

# Run.
main()

# while True:
#     print(state)
#     distance1 = sensor1.distance_cm()
#     distance2 = sensor2.distance_cm()
#     distance3 = sensor3.distance_cm()
#     distance4 = sensor4.distance_cm()
#     
#     print("-----------------------------")
#     print('Distance 1:', distance1, 'cm')
#     print('Distance 2:', distance2, 'cm')
#     print('Distance 3:', distance3, 'cm')
#     print('Distance 4:', distance4, 'cm')
#     
#     sleep(0.1)


