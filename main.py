import serial
from time import sleep
import datetime as dt
import os
import requests
from models.bathroom import Bathroom


#Set Variables
COM = '/dev/ttyACM0'
BAUD = 9600

node_00_open  = b'\x01\t\x00\x04\x00\x02\x03 \x01\xff-'
node_00_close = b'\x01\t\x00\x04\x00\x02\x03 \x01\x00\xd2'

node_01_open  = b'\x01\t\x00\x04\x00\x03\x03 \x01\xff,'
node_01_close = b'\x01\t\x00\x04\x00\x03\x03 \x01\x00\xd3'

data_str = ""

width = 100
cent_width = width - 1

timestart = dt.datetime.now()
currdate = dt.date.today().strftime("%m/%d/%Y")
currtime = dt.datetime.now().strftime("%H:%M:%S")
                 
status     = ["Unk   ","Unk   "]
status_old = ["Unk   ","Unk   "]
time       = [currtime, currtime]
timer      = [timestart, timestart]
encoding = "utf-8"

ser = serial.Serial(COM, BAUD, timeout=0, parity=serial.PARITY_NONE)
if ser.isOpen():
    ser.close()

#set date and time        
def set_date_time():
    global currdate, currtime
    currdate = dt.date.today().strftime("%m/%d/%Y")
    currtime = dt.datetime.now().strftime("%H:%M:%S")

#closes the serial connection
def close():
    if ser.isOpen():
        ser.close()

def logo():
    os.system('clear')
    print()
    print("Operation: TMD".center(cent_width))
    print("*** 01010100 01001101 01000100 *** 01010100 01001101 01000100 ***".center(cent_width))
    print(".___________.  ______     ______  ".center(cent_width))
    print("|           | /  __  \   /  __  \ ".center(cent_width))
    print("`---|  |----`|  |  |  | |  |  |  |".center(cent_width))
    print("    |  |     |  |  |  | |  |  |  |".center(cent_width))
    print("    |  |     |  `--'  | |  `--'  |".center(cent_width))
    print("    |__|      \______/   \______/ ".center(cent_width))
    print("".center(cent_width))
    print(".___  ___.      ___      .__   __. ____    ____ ".center(cent_width))
    print("|   \/   |     /   \     |  \ |  | \   \  /   / ".center(cent_width))
    print("|  \  /  |    /  ^  \    |   \|  |  \   \/   /  ".center(cent_width))
    print("|  |\/|  |   /  /_\  \   |  . `  |   \_    _/   ".center(cent_width))
    print("|  |  |  |  /  _____  \  |  |\   |     |  |     ".center(cent_width))
    print("|__|  |__| /__/     \__\ |__| \__|     |__|     ".center(cent_width))
    print("                                                ".center(cent_width))
    print(" _______   __    __  .___  ___. .______     _______.".center(cent_width))
    print("|       \ |  |  |  | |   \/   | |   _  \   /       |".center(cent_width))
    print("|  .--.  ||  |  |  | |  \  /  | |  |_)  | |   (----`".center(cent_width))
    print("|  |  |  ||  |  |  | |  |\/|  | |   ___/   \   \    ".center(cent_width))
    print("|  '--'  ||  `--'  | |  |  |  | |  |   .----)   |   ".center(cent_width))
    print("|_______/  \______/  |__|  |__| | _|   |_______/    ".center(cent_width))
    
    print()
    print("*** 01010100 01001101 01000100 *** 01010100 01001101 01000100 ***".center(cent_width))
    

def callslack(message):
    API_WEBHOOK = 'https://hooks.slack.com/services/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'
    payload = {'text': message}
    r = requests.post(API_WEBHOOK, json = payload)

def createBathrooms():
    bathroom1 = Bathroom(2, 1, 'unknown')
    bathroom2 = Bathroom(2, 2, 'unknown')
    return [bathroom1, bathroom2]

def run():
    global data_str, currtime, staus, time, status_old, message
    bathrooms = createBathrooms()
    while True:
        currtime = dt.datetime.now().strftime("%H:%M:%S")
        if not ser.isOpen():
            ser.open()
        data = ser.readlines()
        if len(data) > 0:
        #    data_str = data[0].decode(encoding, errors='ignore')        
            if data[0] == node_00_open:
                status[0] = "Opened"
                message = "Bathroom 1 open"
                bathrooms[0].open()
                bathrooms[0].log()
            elif data[0] == node_00_close:
                status[0] = "Closed"
                message = "Bathroom 1 occupado"
                bathrooms[0].close()
                bathrooms[0].log()
            elif data[0] == node_01_open:
                status[1] = "Opened"
                message = "Bathroom 2 open"
                bathrooms[1].open()
                bathrooms[1].log()
            elif data[0] == node_01_close:
                status[1] = "Closed"
                message = "Bathroom 2 occupado"
                bathrooms[1].close()
                bathrooms[1].log()

            if status[0] != status_old[0]:
                changetime = dt.datetime.now()
                timedelta = changetime - timer[0]
                minutes = timedelta.seconds/60
                if minutes > 5 and status[0] == "Opened":
                    message += " WARM SEAT WARNING!!"
                message += " {:.9f}".format(minutes)
                time[0] = currtime
                callslack(message)
                timer[0] = changetime
                status_old[0] = status[0]

            if status[1] != status_old[1]:
                changetime = dt.datetime.now()
                timedelta = changetime - timer[1]
                minutes = timedelta.seconds/60
                if minutes > 5 and status[1] == "Opened":
                    message += " WARM SEAT WARNING!!"
                message += " {:.9f}".format(minutes)
                callslack(message)
                time[1] = currtime
                timer[1] = changetime
                status_old[1] = status[1]

        #print (data_str)
        #print (data)
        logo()
        print(("Current Time: "+currtime).center(cent_width))
        print()
        print(("NODE 00 Status: "+status[0]+" - "+time[0]).center(cent_width))
        print(("NODE 01 Status: "+status[1]+" - "+time[1]).center(cent_width))
        sleep(1)

if __name__ == "__main__":
    run()
