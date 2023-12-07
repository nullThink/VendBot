from flask import Flask, render_template, redirect
from pyairtable import Api
import numpy

import RPi.GPIO as GPIO
# BCM - GPIO Pin Numbers (GPIO `13`)
# BOARD - Actual Pin Numbers (Pin `13`)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
"""
Do this on Pi:
pip3 install 'git+https://github.com/gandalf15/HX711.git#egg=HX711&subdirectory=HX711_Python3'

See this GitHub for reference: https://github.com/gandalf15/HX711/
Then uncomment below import and other code:
"""
#from hx711ToMP import HX711
from hx711Fix import HX711
import time

app = Flask(__name__)

# AirTable Setup
apiToken = #API Token ""
appKey = #App Key ""
tableInventoryKey = #Table Inventory ""

api = Api(apiToken)
table = api.table(appKey, tableInventoryKey)

inventory = []
tableFields = []

for item in table.all():
    inventory.append(item["fields"])

for field in inventory[0]:
    tableFields.append(field)

# print(inventory)

# Transaction State Setup
STANDBY = 0
CALIBRATING = 1
TRANSACTION_STARTED = 2
PAYMENT = 3
ITEM_SELECTION = 4
ITEM_VERIFICATION = 5
FINALIZE_PAYMENT = 6
TRANSACTION_FINISHED = 7

state = STANDBY

class VendingSlot:
    def __init__(self, slotId, scales, solenoidPin) -> None:
        GPIO.setmode(GPIO.BCM)
        # self.scaleSCKPin = scaleSCK
        # self.scaleDataPin = scaleData
        self.solenoidLock = solenoidPin
        self.slotId = slotId
        self.isLocked = True

        # GPIO.setup(scaleSCK, GPIO.IN)
        # GPIO.setup(scaleData, GPIO.IN)
        self.scale1 = scales[0]
        self.scale2 = scales[1]

        self.scale1.zero()
        self.scale2.zero()

        self.calibrated = False

    def zeroScales(self):
        self.scale1.zero()
        self.scale2.zero()

    def getCurrentWeight(self, sampleNums=10):
        # # GPIO.input(self.scaleSCKPin)
        # # GPIO.input(self.scaleDataPin)

        # # Add in load cell measuring code :)
        scale1mean = self.scale1.get_data_mean(sampleNums)
        print(scale1mean)
        scale2mean = self.scale2.get_data_mean(sampleNums)
        print(scale2mean)

        return (scale1mean + scale2mean) / 2
    
    def getIndividualItemWeight(self):
        return int(self.getCurrentWeight() / self.getStock()) 
    
    def getInventory(self):
        inventoryIndex = 0
        indexFound = False

        while(not indexFound):
            if(table.all()[inventoryIndex]["fields"]["Product ID"] == self.slotId):
                indexFound = True
            else:
                inventoryIndex += 1
        
        return table.all()[inventoryIndex]["fields"]
    
    def getStock(self):
        # Get current inventory data
        return self.getInventory()["Stock"]

    def resetCalibration(self):
        recordIndex = 0
        foundId = False
        while(not foundId):
            if(table.all()[recordIndex]["fields"]["Product ID"] == self.slotId):
                foundId = True
            else:
                recordIndex += 1

        recordId = table.all()[recordIndex]["id"]
        # For Note: 9999999 is just an absurdly large value such that
        # for any uncalibrated scales the number of products taken
        # is zero.
        zeroingConstant = 9999999
        table.update(recordId, {"Calibrated Weight": zeroingConstant})

        self.calibrated = False

    def calibrateSingleItem(self):
        newWeight = self.getCurrentWeight(10)

        recordIndex = 0
        foundId = False
        while(not foundId):
            if(table.all()[recordIndex]["fields"]["Product ID"] == self.slotId):
                foundId = True
            else:
                recordIndex += 1

        recordId = table.all()[recordIndex]["id"]
        table.update(recordId, {"Calibrated Weight": newWeight})

        self.calibrate = True

    def getCalibratedSingleItem(self):
        return self.getInventory()["Calibrated Weight"]

    def getScaleDevianceThreshold(self):
        statWeights = []
        for i in range(10):
            statWeights.append(self.getIndividualItemWeight())
        
        return 4 * numpy.std(statWeights)
    
    def updateStock(self, newInventoryValue):
        # Update the inventory data
        recordIndex = 0
        foundId = False
        while(not foundId):
            if(table.all()[recordIndex]["fields"]["Product ID"] == self.slotId):
                foundId = True
            else:
                recordIndex += 1

        recordId = table.all()[recordIndex]["id"]
        table.update(recordId, {"Stock": newInventoryValue})
    
    # Solenoid Locking Functions
    def toggleLock(self):
        if(self.isLocked):
            self.unlock()
        else:
            self.lock()
    
    def lock(self):
        GPIO.setup(self.solenoidLock, GPIO.OUT)
        GPIO.output(self.solenoidLock, False)
        self.isLocked = True
        print("Compartment "+self.slotId+" has been locked.")
    
    def unlock(self):
        GPIO.setup(self.solenoidLock, GPIO.OUT)
        GPIO.output(self.solenoidLock, True)
        self.isLocked = False
        print("Compartment "+self.slotId+" has been unlocked.")

# We already established weigh before opening door -> weigh after opening door
def convertScaleToPricing(itemMass, compartment):

    # Define a threshold for item taking
    # Check for which slots were taken from (compare masses)
    # Calculate how many items were taken from each compartment
    # Find the price for each of the slots taken from
    # Calculate total + display receipt for verification 
    return 0

def alert_pico_motors(movement_flag):
    # Pico will read from pin 8 (GPIO 14)
    # If high, motor can be driven
    # If low, motor power cannot be driven
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(14, GPIO.OUT)

    if(movement_flag):
        GPIO.output(14, True)
    else:
        GPIO.output(14, False)

# GPIO Pin Setup
# # For note: 12 Pins for Vending System Op.

# ------ Solenoids (to enable with L298N Motor Drivers)
lockA1 = 17 # GPIO 17
lockA2 = 27 # GPIO 27
lockB1 = 23 # GPIO 23
lockB2 = 24 # GPIO 24

# ------ Scales (Data, SCK), (HX711 Load Cell Amps.)
scalesA1 = [HX711(20, 21), HX711(26, 19)]
scalesA2 = [HX711(10, 9), HX711(5, 6)]
scalesB1 = [HX711(7, 8), HX711(1, 12)]
scalesB2 = [HX711(18, 25), HX711(16, 4)]

# ----- Unit Setup
unitA1 = VendingSlot("A1", scalesA1, lockA1)
unitA2 = VendingSlot("A2", scalesA2, lockA2)
unitB1 = VendingSlot("B1", scalesB1, lockB1)
unitB2 = VendingSlot("B2", scalesB2, lockB2)

# Flask Setup
global laterPaymentInfo
global compartmentList
global firstRun

firstRun = True

compartmentList = [unitA1, unitA2, unitB1, unitB2]
laterPaymentInfo = ""

# Idea: Add an Update Airtable Entries page

@app.route('/')
def calibration_home():
    global state
    global firstRun
    global compartmentList

    state = CALIBRATING

    if(firstRun):
        for product in compartmentList:
            product.resetCalibration()

    calibrationHomePage = """
    <h1>Calibrated Weight for A1: {0}</h1>
    <h1>Calibrated Weight for A2: {1}</h1>
    <h1>Calibrated Weight for B1: {2}</h1>
    <h1>Calibrated Weight for B2: {3}</h1>

    <a href="/calibrate/A1"><button>Calibrate A1</button></a>
    <a href="/calibrate/A2"><button>Calibrate A2</button></a>
    <a href="/calibrate/B1"><button>Calibrate B1</button></a>
    <a href="/calibrate/B2"><button>Calibrate B2</button></a>
    <a href="/running"><button>Finish</button></a>
    """

    calibratedWeights = []
    for product in compartmentList:
        calibratedWeights.append(product.getCalibratedSingleItem())
    
    alert_pico_motors(False)
        
    return calibrationHomePage.format(calibratedWeights[0], calibratedWeights[1], calibratedWeights[2], calibratedWeights[3])

@app.route('/calibrate/<compartment_id>')
def calibrate(compartment_id):
    global state
    global firstRun
    global compartmentList
    
    firstRun = False
    state = CALIBRATING
    currentComp = ""

    for compartment in compartmentList:
        if(compartment.slotId == compartment_id):
            currentComp = compartment
    
    currentComp.calibrateSingleItem()
    #print(currentComp.getCalibratedSingleItem())

    calibrationPage = """
    <h1>Calibrated Weight for Compartment {0}: {1}</h1>
    <a href='/calibrate/A1'><button>Retry Calibration</button></a>
    <a href='/'><button>Lock In Weight</button></a>
    """
    return calibrationPage.format(compartment_id, currentComp.getCalibratedSingleItem())

@app.route('/running')
def base_state():
    global state
    state = STANDBY
    alert_pico_motors(True)
    
    return render_template("base.html")

@app.route('/payment')
def payment():
    global state
    state = PAYMENT
    alert_pico_motors(False)

    ## THIS SEEMS UNRELIABLE BUT FOR PURPOSES: 
    # https://venmo.readthedocs.io/en/latest/
    # https://pypi.org/project/venmo-api/

    # Ask for payment method storing. (Ask for Venmo?)
    # Store for later
    #parsed_items = parse_cart_items(cart_items)

    # For page button, send venmo as part of system 
    return render_template("payment.html")

global preVendWeight
global postVendWeight 

preVendWeight = []
postVendWeight = []

@app.route('/grab_items/<stored_venmo>')
def pre_item_selection(stored_venmo):
    global laterPaymentInfo
    global state
    global compartmentList
    global preVendWeight

    preVendWeight = []

    laterPaymentInfo = stored_venmo
    state = ITEM_SELECTION
    
    # Weigh scales before unlocking solenoids
    # Unlock solenoids
    for compartment in compartmentList:
        preVendWeight.append(compartment.getCurrentWeight())
        compartment.unlock()
    # Wait for user to finish (remind to close all lids before finishing)
    return render_template("vending.html")

@app.route('/verify_items')
def item_verification():
    global state
    global compartmentList
    global postVendWeight

    state = ITEM_VERIFICATION
    postVendWeight = []

    # Relock solenoids
    # Weigh scales again
    for compartment in compartmentList:
        postVendWeight.append(compartment.getCurrentWeight())
        compartment.lock()

    weightDifferences = []

    for idx in range(len(preVendWeight)):
        weightDifferences.append(preVendWeight[idx] - postVendWeight[idx])

    numItemsTaken = []
    priceItemsTaken = []
    i=0

    # Find how many items were taken
    # Get prices

    for product in compartmentList:
        currCalibratedWeight = product.getCalibratedSingleItem()
        numItemsTaken.append(round(weightDifferences[i] / currCalibratedWeight))
        priceItemsTaken.append({"unrounded_count":weightDifferences[i] / currCalibratedWeight,"name":product.getInventory()["Item Name"], 
                              "cost": numItemsTaken[i] * float(product.getInventory()["Price"])
                              })
        i+=1
 
    # Display to user to ask if amount is correct

    itemList = """
    <!DOCTYPE html>

    <head>
    <title>Document</title>
    <style>
        h1 {
            font-family: 'Arial', Courier, monospace;
        }
    </style>
    </head>
    <body>
    <div style="text-align: center; width: 65%; margin: 0 auto; background-color:#D0F1BF; border-radius:5px; padding:5%; margin-top: 5%;">
    """

    for item in priceItemsTaken:
        #itemList = itemList + "<h1>{0}: ${1}, Quantity: {2}</h1>".format(item["name"], item["cost"], item["unrounded_count"])
        itemList = itemList + "<h1>{0}: ${1}</h1>".format(item["name"], item["cost"])

    receipt = itemList + """
        <h1><i><u><strong>Is this correct?</strong></u></i></h1>
        <a href="/finish"><button style="padding:10px; width:100%; background-color: #9ABD97; border-radius: 5px; border:none; font-size: 20px;"><strong>Yes</strong></button></a>
    </div>
    </body>
    """
    return receipt

@app.route('/finish')
def finish_transaction():
    global state
    global laterPaymentInfo

    # Send venmo request to user
    # Make sure request is fulfilled (unsure if possible?)
    state = TRANSACTION_FINISHED

    # Send a thanks for using system
    # Notify user that the robot will start moving again soon
    # # ^^ This is handled in the render_template html with timeout
    # Fetch running state
    # Send through serial to Pico W that it can move again

    return render_template("thanks_to_warn.html")

GPIO.cleanup()


"""
Some of this is deprecated, based on an older concept 
that we're not going with anymore.
"""
# Flask Setup

# app = Flask(__name__)

# def parse_cart_items(cart_string):
#     itemList = []
#     for i in range(int(len(cart_string)/2)):
#         cart_item = cart_string[0+i*2:0+(i*2)+2]
#         itemList.append(cart_item)
#     return itemList

# @app.route('/')
# def base_state():
#     return Flask.render_template("index.html")

# @app.route('/cart/<cart_items>')
# def state_cart(cart_items):
#     parsed_items = parse_cart_items(cart_items)
#     return 'Cart state'
