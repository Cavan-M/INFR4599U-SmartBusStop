import vision
import time
import random
import os
from I2C_LCD import lcd
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
import dht11
import RPi.GPIO as GPIO
import threading
from google.transit import gtfs_realtime_pb2
from math import floor

# Simple Pin control
class SimplePIN:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)


relay = SimplePIN(26)

#stop number in the DB
stop_number = 1009

# delay in seconds between photos of people leaving the bus
BURST_DELAY = 2
# delay in seconds to capture waiting patrons after the bus leaves
EXIT_DELAY = 10
# this value represents 1 / calls per second,  too low value may cause the LCD to change too quickly
LISTEN_DELAY = 1


# Display welcome splash screen
stop_display = lcd()
stop_display.lcd_display_string("      Welcome       ", 1)
stop_display.lcd_display_string("                    ", 2)
time.sleep(2)

cred = credentials.Certificate('bus-stop-81be5-firebase-adminsdk-o0oe4-777c936f7b.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://bus-stop-81be5-default-rtdb.firebaseio.com/"
})

# Use google vision to calculate number of bus riders
def count_offboarding(busData):
    people_counter = vision.PeopleCounter()
    count = 0
    randString = str(random.randint(999999,1999999))
    filenames = []
    for x in range(0,5):
        filename = "/tmp/busimages/" + randString + str(x) +  ".jpg"
        execute_string = 'fswebcam -r 1280x720 ' + filename
        os.system(execute_string)
        filenames.append(filename)
        time.sleep(BURST_DELAY)
    
    for filename in filenames:
        current_count = people_counter.count_people(filename)
        if current_count > count:
            count = current_count

    time.sleep(EXIT_DELAY)
    waiting_after = count_waiting_people()
    
    waiting_before = db.reference("/stops/" + str(stop_number)).get()['waiting']
    off_boarded = count - waiting_before
    on_boarded = waiting_before - waiting_after
    riders = int(busData['occupants']) - off_boarded + on_boarded

    return riders


# Use Google Cloud Vision to count people waiting at the bus stop
def count_waiting_people():
    people_counter = vision.PeopleCounter()
    randString = str(random.randint(999999,1999999))
    filename = "/tmp/busimages/" + randString + ".jpg"
    execute_string = 'fswebcam -r 1280x720 ' + filename
    os.system(execute_string)
    time.sleep(1)
    count = people_counter.count_people(filename)
    return count

# Handle updates received from Firebase
def listener(event):
    
    if event.path != "/":
        dat = db.reference('/buses' + event.path[0:8]).get()
        if dat["nextStop"] == stop_number:
            stop_display.lcd_display_string(dat['route'] + " ETA: " + str(dat['arrival']) + "min", 1)
            stop_display.lcd_display_string("%.2f" %((dat['occupants']/dat['capacity'])*100) + "% Capacity", 2)
            time.sleep(LISTEN_DELAY)
            db.reference('/stops/'+str(stop_number)+'/').update({'waiting': count_waiting_people()})
        elif dat["nextStop"] == int(str(stop_number)+'101'):
            updated_rider_count = count_offboarding(dat)
            db.reference('/buses' + event.path[0:8]).update({'occupants': int(updated_rider_count)})

def update_eta():
    tta=10000
    feed = gtfs_realtime_pb2.FeedMessage()
    os.system("wget 'https://drtonline.durhamregiontransit.com/gtfsrealtime/TripUpdates'")
    with open('TripUpdates','rb') as f:
        buff = f.read()
    feed.ParseFromString(buff)
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            if entity.trip_update.trip.route_id == "901":
                for update in entity.trip_update.stop_time_update:
                    if update.stop_id == "698:1":
                        if floor((update.arrival.time -time.time())/60) <= tta and floor((update.arrival.time -time.time())/60) >= 0: 
                            tta = floor((update.arrival.time -time.time())/60) 
    
    os.system("rm -f /home/cavanramis2/final/busstop/TripUpdates")
    return tta


def update_thread():
    while True:
        eta = update_eta()
        temperature = dht11.main()
        if temperature != None and temperature < 8:
            relay.on()
        elif temperature != None and temperature > 20:
            relay.off()
        db.reference('/buses/bus0001/').update({ 'arrival': eta})
        time.sleep(30)


# New thread for updating values
auto_update = threading.Thread(target=update_thread)
auto_update.start()

# Listen to updates to /buses
db.reference('/buses').listen(listener)



