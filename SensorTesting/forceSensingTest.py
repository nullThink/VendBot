import machine
from hx711 import HX711
import time
#from scales import Scales

sck = 12
data = 13

loadAmp = HX711(data, sck)
#loadAmp.power_up()
#loadAmp.tare()
#scale = Scales(data, clock)
#scale.tare()

while True:
    print(loadAmp.read())
    time.sleep(0.1)
    #print(scale.stable_value())