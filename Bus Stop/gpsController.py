#! /usr/bin/python
from gps import *
import time
import math

class simple_gps:
    def __init__(self):
        self.gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 
        self.latitude = None
        self.longitude = None
        self.coords = (self.latitude, self.longitude)
        
    def __str__(self):
        printstr = ""
        if self.latitude == None:
            loc = self.get_coords()
        if self.latitude > 0:
            printstr += str(self.latitude) + u'8\N{DEGREE SIGN}' + " N  "
        else:
             printstr += str(abs(self.latitude)) + u'8\N{DEGREE SIGN}' + " S, "
        if self.longitude > 0:
            printstr += str(self.longitude) + u'8\N{DEGREE SIGN}' + " E"
        else: printstr += str(abs(self.longitude)) + u'8\N{DEGREE SIGN}' + " W"
        return printstr

    def get_coords(self):
        report = self.gpsd.next()
        if report['class'] == 'TPV':
            self.latitude, self.longitude = getattr(report,'lat',None), getattr(report,'lon',None)
        if self.latitude == None:
            time.sleep(0.3)
            self.get_coords()
        else: 
            self.coords = (self.latitude, self.longitude)
            return self.coords
    
    def get_latitude(self):
        return self.get_coords()[0]
    
    def get_longitude(self):
        return self.get_coords()[1]

if __name__ == '__main__':
    mygps = simple_gps()
    print(mygps)
    print(mygps.get_coords())


    
    