# Simple enough, just import everything from tkinter.
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from urllib.request import urlopen, Request
import requests
import time
#import json

import platform
if platform.node() == 'raspberrypi':
    use_device = True
else:
    use_device = False

if use_device:
    import RPi.GPIO as GPIO
    # variables initialization
    # Light pin assignment
    PIN = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

auto_upload_trigger = time.time()

# light 1 related variables
light_1_initialize_flag = 0

current_temperature_setting = 20
waiting_status = 0

light_1_running = 0
light_1_not_running = 0
light_1_start = 0
light_1_off = 0

light_1_time_upload_last = time.time()
light_1_time_upload_now = time.time()

light_1_status = 0

# uploading related variables
baseURL_light_running = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field1=0'
baseURL_light_off = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field2=0'


UPDATE_RATE = 500


def uploading_light_running_time():
    global light_1_time_upload_now
    global light_1_time_upload_last
    global light_1_running
    global baseURL_light_running
    light_1_time_upload_now = time.time()

    if (light_1_time_upload_now - light_1_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_running + str(light_1_running))
        print(f.content)
        print('uploading succeed')
        light_1_time_upload_last = light_1_time_upload_now
        light_1_running = 0
    else:
        print('not uploading because of the limitation of ThingSpeak')


def uploading_light_off_time():
    global light_1_time_upload_now
    global light_1_time_upload_last
    global light_1_not_running
    global baseURL_light_off
    light_1_time_upload_now = time.time()
    if (light_1_time_upload_now - light_1_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_off + str(light_1_not_running))
        print(f.content)
        print('uploading succeed')
        light_1_time_upload_last = light_1_time_upload_now
        light_1_not_running = 0
    else:
        print('not uploading because of the limitation of ThingSpeak')


def open_light():
    global light_1_start
    global light_1_off
    global light_1_status
    global light_1_not_running
    global light_1_initialize_flag
    if light_1_status == 1:
        print("light is already on, do nothing")
    else:
        if use_device:
            GPIO.output(PIN, GPIO.HIGH)
        print("light on")
        light_1_status = 1
        panel_status.set('10')
        light_1_start = time.time()
        if light_1_initialize_flag == 0:
            light_1_initialize_flag = 1
            light_1_off = light_1_start
        light_1_not_running += (light_1_start - light_1_off)
        print('light #1\'s total off time is ' + str(round(light_1_not_running)) + ' seconds')
        uploading_light_off_time()


def close_light():
    global light_1_running
    global light_1_start
    global light_1_off
    global light_1_status
    if light_1_status == 0:
        print("light is already closed, do nothing")
    else:
        if use_device:
            GPIO.output(PIN, GPIO.LOW)
        print("light off")
        light_1_status = 0
        panel_status.set('00')
        light_1_off = time.time()
        light_1_running += (light_1_off - light_1_start)
        print('light #1\'s total on time is '  + str(round(light_1_running)) + ' seconds')
        uploading_light_running_time()


def decode_light(command):
    if command == "00":
        close_light()
    elif command == "01":
        open_light()
    else:
        print("invalid light instruction")


def decode_ac(command):
    if command == "000":
        print("air-conditioner off")
        temperature.set("Off")
    elif command == "010":
        print("air-conditioner on")
    elif command[0] == "1":
        current_temperature_setting = int(command[1:3])
        temperature.set(str(current_temperature_setting) + u'\N{DEGREE SIGN}'+'C')
        print("temperature setting is changed to: ", current_temperature_setting)
    else:
        print("invalid AC instruction")


class Application(tk.Frame):
    """ GUI """
    def __init__(self, master):
        """ Initialize the Frame"""
        tk.Frame.__init__(self, master)
        self.load_1 = Image.open("Bosch_Control_Panel_Cropped_1.jpg")
        self.load_2 = Image.open("Bosch_Control_Panel_Cropped_2.jpg")
        self.load_3 = Image.open("Bosch_Control_Panel_Cropped_3.jpg")
        self.load_4 = Image.open("Bosch_Control_Panel_Cropped_4.jpg")
        self.render = ImageTk.PhotoImage(self.load_1)
        self.img = Label(self, image=self.render, textvariable=temperature, compound=tk.CENTER)
        self.img.image = self.render
        self.labelfont = labelfont = ('times', 100, 'bold')
        self.img.config(font=self.labelfont)
        self.img.config(fg='white')

        self.grid()
        self.create_widgets()
        self.updater()

    def create_widgets(self):
        self.master.title("Room Local Monitor")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)

        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="Program", menu=file)

        self.img.pack()

    def read_instruction(self):
        global light_1_not_running
        global light_1_off
        global auto_upload_trigger
        global  light_1_running
        global light_1_start
        if (time.time() - auto_upload_trigger) > 60:
            if light_1_status == 0:
                light_1_not_running = time.time() - light_1_off
                uploading_light_off_time()
                light_1_off = time.time()
            elif light_1_status == 1:
                light_1_running = time.time() - light_1_start
                uploading_light_running_time()
                light_1_start = time.time()
            auto_upload_trigger = time.time()
        else:
            request = Request('https://api.thingspeak.com/talkbacks/31641/commands/execute?api_key=NU6M3B6JB1Q3IR76')
            response = urlopen(request)
            command = response.read().decode()
            '''
            command code:
            [device type(1)][control instruction(2)]
            device type: 0 - lighting system
                         1 - air-conditioner
            000: light off
            001: light on
            1000: air-conditioner off
            1010: air-conditioner on
            11xx: air-conditioner set to xx degrees
            '''
            global waiting_status
            if not command:
                if waiting_status == 0:
                    waiting_status = 1
                    print("waiting for commands...")
                    pass
                else:
                    pass
            else:
                waiting_status = 0
                if command[0] == '0':
                    decode_light(command[1:3])

                elif command[0] == '1':
                    decode_ac(command[1:4])

                else:
                    print("invalid instruction")
            status_tmp = panel_status.get()
            if status_tmp == 0:
                self.render = ImageTk.PhotoImage(self.load_1)
            elif status_tmp == 10:
                self.render = ImageTk.PhotoImage(self.load_2)
            elif status_tmp == 1:
                self.render = ImageTk.PhotoImage(self.load_3)
            else:
                self.render = ImageTk.PhotoImage(self.load_4)
            self.img.config(image=self.render)

    def updater(self):
        self.read_instruction()
        self.create_widgets()
        self.after(UPDATE_RATE, self.updater)

    def client_exit(self):
        global light_1_status
        global light_1_off
        global light_1_running
        global light_1_not_running
        if light_1_status == 1:
            if use_device:
                GPIO.output(PIN, GPIO.LOW)
            print("light off")
            light_1_status = 0
            light_1_off = time.time()
            light_1_running += (light_1_off - light_1_start)
        else:
            light_1_not_running += (time.time() - light_1_off)
        uploading_light_running_time()
        uploading_light_off_time()
        exit()


root = tk.Tk()
temperature = IntVar()
temperature.set('Off')
panel_status = IntVar()
panel_status.set(0)
root.title("monitor")
root.geometry("1237x761")
app = Application(root)
root.mainloop()
