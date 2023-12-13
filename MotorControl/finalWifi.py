# Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
from hcsr04 import HCSR04
import time
import uasyncio as asyncio
import machine

# Serial Setup
fauxSerial = machine.Pin(9, machine.Pin.IN) # Set actual "serial" pin

# Distance Sensor Setup
sensor1 = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=10000)
sensor2 = HCSR04(trigger_pin=5, echo_pin=19, echo_timeout_us=10000)
sensor3 = HCSR04(trigger_pin=5, echo_pin=20, echo_timeout_us=10000)
sensor4 = HCSR04(trigger_pin=5, echo_pin=21, echo_timeout_us=10000)

# State Setup
RUNNING = 0
STOPPED = 1

global state
state = RUNNING

# Coroutine Setup
import network
import socket
from secrets import *

ssid = tuftsWifi["user"]
password = tuftsWifi["pass"]

# ssid = personalWifi["user"]
# password = personalWifi["pass"]

async def serve(connection):
    # Motor Driver Setup
    
    # Motor 1 !! Set pins later during setup
    motorA1 = machine.Pin(28, machine.Pin.OUT)
    motorA2 = machine.Pin(27, machine.Pin.OUT)
    motorAPWM = machine.Pin(25)
    
    aSignal = machine.PWM(motorAPWM, freq=500, duty_u16=32768)

    # Motor 2 !! Set pins later during setup
    motorB1 = machine.Pin(26, machine.Pin.OUT)
    motorB2 = machine.Pin(23, machine.Pin.OUT)
    motorBPWM = machine.Pin(24)
    
    bSignal = machine.PWM(motorBPWM, freq=500, duty_u16=32768)

    while True:
        try:
            client, address = connection.accept()
            request = client.recv(1024)
            request = str(request)
            
            #print(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass
            
            if request == '/forward' and state==RUNNING:
                motorA1.high()
                motorB1.high()
                
                motorA2.low()
                motorB2.low()
            elif request =='/backward' and state==RUNNING:
                motorA1.low()
                motorB1.low()
                
                motorA2.high()
                motorB2.high()
            elif request == '/left' and state==RUNNING:
                motorA1.high()
                motorB1.low()
                
                motorA2.low()
                motorB2.high()
            elif request =='/right' and state==RUNNING:
                motorA1.low()
                motorB1.high()
                
                motorA2.high()
                motorB2.low()
            else:
                motorA1.low()
                motorB1.low()
                
                motorA2.low()
                motorB2.low()
                
            html = webpage()
            client.send(html)
            
            client.close()

        except OSError as e:
            client.close()
            print('Connection closed')
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print(wlan.ifconfig())
    return wlan.ifconfig()
    
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage():
    html = """
            <!DOCTYPE html>
            <head>
            <title>Document</title>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
            let currentURL = window.location.href;
            const RESET_LINK = "http://10.245.145.146:5000/";

            let buttonHeld;

            window.onload = (e) => {

            document.addEventListener("keydown", (e) => {
            if(e.code == "KeyW"){
            $.get("/forward");
            console.log("Up");      
            }
            else if(e.code == "KeyS"){
                $.get("/backward");
                console.log("Down");      
            }
            else if(e.code == "KeyA"){
                $.get("/left");
                console.log("Left");      
            }
            else if(e.code == "KeyD"){
                $.get("/right");
                console.log("Right");      
            }
            else if(e.code == "Space"){
                $.get("/dispense");
                console.log("Dispensing...");
            }
            else{
                $.get("/");
                console.log("Unrecognized");
            }

            });

            document.addEventListener("keyup", (e) => {
            $.get("/");
            });
            }
            </script>
            </head>
            <body>

            </body>
            </html>
            """
    return html

# For Testing
async def motorRun():
    global state
    global fauxSerial
    
    while True:
        fauxSerialValue = fauxSerial.value()
        #print("Motor")
        
        #print("State: " + str(state))
        
        if(not fauxSerialValue or state == STOPPED):
            state = STOPPED
            print(state)
            #motorActivePin.value(False)
        elif(state == RUNNING or fauxSerialValue):
            state = RUNNING
            print(state)
            #motorActivePin.value(True)
            
        await asyncio.sleep(0.1)

async def sensor1Check():
    global state
    
    while True:
        #print("S1")
        currentDistance = sensor1.distance_cm()
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

async def sensor2Check():
    global state
    
    while True:
        #print("S2")
        currentDistance = sensor2.distance_cm()
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

async def sensor3Check():
    global state
    
    while True:
        #print("S3")
        currentDistance = sensor3.distance_cm()

        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING

        await asyncio.sleep(0.1)

async def sensor4Check():
    global state
    
    while True:
        #print("S4")
        currentDistance = sensor4.distance_cm()
        print(str(currentDistance))
        
        if(currentDistance <= 5):
            state = STOPPED
        else:
            state = RUNNING
        
        await asyncio.sleep(0.1)

"""
# Not Working
# async def taskSetup():
#     sensor1Task = asyncio.create_task(sensor1Check())
#     sensor2Task = asyncio.create_task(sensor2Check())
#     sensor3Task = asyncio.create_task(sensor3Check())
#     sensor4Task = asyncio.create_task(sensor4Check())
# 
#     motorTask = asyncio.create_task(motorRun())
"""

# Main Setup
def main():
    try:
        connection = ""
    
        ip = connect()
        ip = ip[0]
        connection = open_socket(ip)
            
        # Get a permanently running event loop
        loop = asyncio.get_event_loop()

        internetTask = loop.create_task(serve(connection))
        sensor1Task = loop.create_task(sensor1Check())
        sensor2Task = loop.create_task(sensor2Check())
        sensor3Task = loop.create_task(sensor3Check())
        sensor4Task = loop.create_task(sensor4Check())

        motorTask = loop.create_task(motorRun())

        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        print("Stopped (Connection)")
    except OSError as e:
        cl.close()
        print('Connection closed')

# Run.
try:
    main()
except KeyboardInterrupt:
    machine.reset()
    print("Stopped (Main)")
except OSError as e:
    cl.close()
    print('Connection closed')

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



