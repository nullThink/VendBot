# Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
from hcsr04 import HCSR04
from time import sleep

# ESP32
sensor1 = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=10000)
sensor2 = HCSR04(trigger_pin=5, echo_pin=19, echo_timeout_us=10000)
sensor3 = HCSR04(trigger_pin=5, echo_pin=20, echo_timeout_us=10000)
sensor4 = HCSR04(trigger_pin=5, echo_pin=21, echo_timeout_us=10000)

# ESP8266
#sensor = HCSR04(trigger_pin=12, echo_pin=14, echo_timeout_us=10000)

while True:
    distance1 = sensor1.distance_cm()
    distance2 = sensor2.distance_cm()
    distance3 = sensor3.distance_cm()
    distance4 = sensor4.distance_cm()
    
    print("-----------------------------")
    print('Distance 1:', distance1, 'cm')
    print('Distance 2:', distance2, 'cm')
    print('Distance 3:', distance3, 'cm')
    print('Distance 4:', distance4, 'cm')
    
    sleep(0.1)

