# Bus Number 0001

import time
import random
from I2C_LCD import lcd
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
import gpsController
import threading

# USE THIS VALUE TO TWEEK GPS ACCURACY
# lower values are good with an accurate GPS
# higher values are good with an inaccurate GPS, but might cause issues with camera timings
GPS_TOLERANCE = 0.0001

# Time in seconds between updates
UPDATE_FREQUENCY = 5


# Display welcome splash screen
stop_display = lcd()
stop_display.lcd_display_string("    Welcome       ", 1)
stop_display.lcd_display_string("                    ", 2)
time.sleep(2)

locator = gpsController.simple_gps()

cred = credentials.Certificate('bus-stop-81be5-firebase-adminsdk-o0oe4-777c936f7b.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://bus-stop-81be5-default-rtdb.firebaseio.com/"
})


# Estimate the time until arrival at the next bus stop
def estimate_arrival():
    # TODO: Use gps module in conjunction with a maps api to get estimated time of arrival in minutes
    # below is a placeholder
    return 10

def increment_stop():
    coordinates = locator.get_coords()
    print(coordinates)
    latitude = locator.latitude
    longitude = locator.longitude
    
    next_stop = db.reference("/buses/bus0001").get()['nextStop']
    stop_data = db.reference("/stops/" + str(db.reference("/buses/bus0001").get()['nextStop'])).get()
    print(stop_data)
    route = db.reference("/routes/" + str(db.reference("/buses/bus0001").get()['route'])).get()
    try:
        upper_lon = stop_data['lon']+GPS_TOLERANCE
        lower_lon = stop_data['lon']-GPS_TOLERANCE
        upper_lat = stop_data['lat']+GPS_TOLERANCE
        lower_lat = stop_data['lat']-GPS_TOLERANCE
        try:
            next_next_stop = int({i for i in route if route[i]==route[str(next_stop+1)]}.pop())
            

        except KeyError:
            next_next_stop = int({i for i in route if route[i]==1}.pop())
        
    
        if next_next_stop:
            if latitude < upper_lat and latitude > lower_lat and longitude > lower_lon and longitude < upper_lon:
                indicator = int(str(next_stop) + '101')
                db.reference('/buses/bus0001/').update({'nextStop': indicator})
                time.sleep(20)
                db.reference('/buses/bus0001/').update({'nextStop': next_next_stop})
    except IndexError:
        pass
    '''             
    except TypeError:
        print("Stop", next_stop, "Doesn't Exist but is specified in the route")
        print("I think this is because of a shutdown, defaulting to route beginning")
        next_next_stop = int({i for i in route if route[i]==1}.pop())
        db.reference('/buses/bus0001/').update({'nextStop': next_next_stop})

    '''
# Handle updates received from Firebase
def listener(event):
    if event.path != "/":
        ref = db.reference("/buses/bus0001").get()
        if event.path[1:] == str(ref['nextStop']):
            stop_display.lcd_display_string(" Next stop has   ", 1)
            if event.data['waiting'] == 1:
                stop_display.lcd_display_string(str(event.data['waiting']) + " Passenger", 2)
            else:
                stop_display.lcd_display_string(str(event.data['waiting']) + " Passengers", 2)
        else:
            print(event.path[1:], " =/= ", str(ref['nextStop']))

# Update thread function
def update_status():
    while True:
        eta = estimate_arrival()
        increment_stop()
        db.reference('/buses/bus0001/').update({ 'arrival': eta})
        time.sleep(UPDATE_FREQUENCY)

# New thread for updating values
auto_update = threading.Thread(target=update_status)
auto_update.start()

# Init display with defaul values
stop_display.lcd_display_string(" Next stop has   ", 1)
stop_display.lcd_display_string( str(db.reference("/stops/" + str(db.reference("/buses/bus0001").get()['nextStop'])).get()['waiting']) + " Passengers", 2)

# Listen to updates to /stops
firebase_admin.db.reference('/stops').listen(listener)

