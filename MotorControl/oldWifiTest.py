import network
import socket
import time
import machine
from secrets import *

ssid = tuftsWifi["user"]
password = tuftsWifi["pass"]

# ssid = personalWifi["user"]
# password = personalWifi["pass"]
MAX_DUTY = 65535

def serve(connection):
    # Motor Driver Setup
    
    # Motor 1 !! Set pins later during setup
    motorA1 = machine.Pin(18, machine.Pin.OUT)
    motorA2 = machine.Pin(19, machine.Pin.OUT)
    motorAPWM = machine.Pin(4)
    
    aSignal = machine.PWM(motorAPWM, freq=500, duty_u16=int(MAX_DUTY*0.5))

    # Motor 2 !! Set pins later during setup
    motorB1 = machine.Pin(20, machine.Pin.OUT)
    motorB2 = machine.Pin(21, machine.Pin.OUT)
    motorBPWM = machine.Pin(5)
    
    bSignal = machine.PWM(motorBPWM, freq=500, duty_u16=int(MAX_DUTY*0.5))

    while True:
        try:
            client = connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            
            print(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass
            if request == '/forward':
                motorA1.high()
                motorB1.high()
                    
                motorA2.low()
                motorB2.low()
            elif request =='/backward':
                motorA1.low()
                motorB1.low()
                
                motorA2.high()
                motorB2.high()
            elif request == '/left':
                motorA1.high()
                motorB1.low()
                
                motorA2.low()
                motorB2.high()
            elif request =='/right':
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
        except KeyboardInterrupt:
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
    
try:
    ip = connect()
    ip = ip[0]
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
except OSError as e:
    cl.close()
    print('Connection closed')
