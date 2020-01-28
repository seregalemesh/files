#!/usr/bin/python
# -*- coding: utf-8

import MySQLdb
import time
import RPi.GPIO as GPIO
from threading import Thread
import datetime as Datetime
import gc

class LedsThread(Thread):

    global thread_refresh

    global db
    global cursor

    def __init__(self, mode, balance, OUTPUTS, RELOUTS, IN_PIN_SECURITY, interval_service, time_service, relays_thread):
        Thread.__init__(self)  

        gc.enable()

        self.thread_refresh = False

        self.mode = mode
        self.balance = balance
        self.IN_PIN_SECURITY = IN_PIN_SECURITY
        self.OUTPUTS = OUTPUTS
        self.RELOUTS = RELOUTS
        self.interval_service = interval_service
        self.time_service = time_service
        self.relays_thread = relays_thread

        #self.db = MySQLdb.connect(host="localhost", user="root", passwd="23111983", db="vending", charset='utf8')
        #self.cursor = self.db.cursor()

    def run(self):
        while True :
            self.thread_refresh = False

            for gpio_out in range(len(self.OUTPUTS)):
                GPIO.output(self.OUTPUTS[gpio_out], GPIO.LOW)

            while self.thread_refresh == False and int(self.balance) == 0:               
                if GPIO.input(self.IN_PIN_SECURITY) == True :

                    try:
                            self.db = MySQLdb.connect(host="localhost", user="root", passwd="23111983", db="vending", charset='utf8')
                            self.cursor = self.db.cursor()

                            self.cursor.execute("SELECT * FROM `service_stats` ORDER BY `id` DESC LIMIT 1")
                            records = self.cursor.fetchall()

                            nt = Datetime.datetime.now()
                            ndt = int(time.mktime(nt.timetuple()))
                                                        
                            for row in records :
                                id, last_start = row

                                st = False
                                #print "datetime: ", ndt - int(time.mktime(last_start.timetuple()))
                                if ndt - int(time.mktime(last_start.timetuple())) > self.interval_service :
                                    self.relays_thread.service(self.time_service)
                                    st = True

                            if st == True :
                                self.cursor.execute("INSERT INTO service_stats (id, last_start) VALUES (NULL, NULL)")
                                self.db.commit()

                            db.close()
                    except:
                    
                        print "Error service"

                    gc.collect()
                    time.sleep(2)

                for gpio_out in range(len(self.OUTPUTS)):
                    if gpio_out != 6 and gpio_out != 0  :
                        if self.thread_refresh == False and int(self.balance) == 0:
                            GPIO.output(self.OUTPUTS[gpio_out], GPIO.HIGH)
                        if self.thread_refresh == False and int(self.balance) == 0:
                            time.sleep(0.5)
                        if self.thread_refresh == False and int(self.balance) == 0:
                            GPIO.output(self.OUTPUTS[gpio_out], GPIO.LOW)
                    else :
                        if gpio_out == 0 :
                            if self.thread_refresh == False and int(self.balance) == 0:
                                GPIO.output(self.OUTPUTS[6], GPIO.HIGH)
                            if self.thread_refresh == False and int(self.balance) == 0:
                                time.sleep(0.5)
                            if self.thread_refresh == False and int(self.balance) == 0:
                                GPIO.output(self.OUTPUTS[6], GPIO.LOW)

                        if gpio_out == 6 :
                            if self.thread_refresh == False and int(self.balance) == 0:
                                GPIO.output(self.OUTPUTS[0], GPIO.HIGH)
                            if self.thread_refresh == False and int(self.balance) == 0:
                                time.sleep(0.5)
                            if self.thread_refresh == False and int(self.balance) == 0:
                                GPIO.output(self.OUTPUTS[0], GPIO.LOW)

            while self.thread_refresh == False and int(self.balance) > 0: 
                GPIO.output(self.OUTPUTS[int(self.mode)], GPIO.HIGH)

                for gpio_out in range(len(self.OUTPUTS)):
                    if gpio_out != int(self.mode):
                        GPIO.output(self.OUTPUTS[gpio_out], GPIO.LOW)

                while self.thread_refresh == False :
                    time.sleep(0.5)

    def refresh_mode(self, mode) :
        self.mode = mode
        self.thread_refresh = True

    def refresh_balance(self, balance) :
        self.balance = balance
        self.thread_refresh = True
