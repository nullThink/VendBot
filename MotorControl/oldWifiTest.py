import network
import socket
import time
import machine
from secrets import *

ssid = tuftsWifi["user"]
password = tuftsWifi["pass"]

# ssid = personalWifi["user"]
# password = personalWifi["pass"]

def serve(connection):
    # Motor 1
    in1 = machine.Pin(10, machine.Pin.OUT)
    in2 = machine.Pin(11, machine.Pin.OUT)

    # Motor 2
    in3 = machine.Pin(12, machine.Pin.OUT)
    in4 = machine.Pin(13, machine.Pin.OUT)
    
    # Servo Motor + PWM Setup
    servoSignal = machine.Pin(6, machine.Pin.OUT)

    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/forward':
            in1.value(1)
            in2.value(0)
            
            in3.value(1)
            in4.value(0)
        elif request =='/backward':
            in1.value(0)
            in2.value(1)
            
            in3.value(0)
            in4.value(1)
        elif request == '/left':
            in1.value(0)
            in2.value(1)
            
            in3.value(1)
            in4.value(0)
        elif request =='/right':
            in1.value(1)
            in2.value(0)
            
            in3.value(0)
            in4.value(1)
        else:
            in1.value(0)
            in2.value(0)
            
            in3.value(0)
            in4.value(0)
        html = webpage()
        client.send(html)
        
        client.close()
    
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

