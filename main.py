# Import tkinter related stuff
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

# Import other libs
from urllib.request import urlopen, Request
import requests
import time
# import json

# Check if it is running on raspberry pi
import platform
if platform.node() == 'raspberrypi':
    use_device = True
else:
    use_device = False

# Initialize GPIO if it is running on raspberry pi
if use_device:
    import RPi.GPIO as GPIO
    # variables initialization
    # Light pin assignment
    PIN_1 = 20
    PIN_2 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_1, GPIO.OUT)
    GPIO.setup(PIN_2, GPIO.OUT)

# loop related variable
waiting_status = 0
auto_upload_trigger = time.time()

# current_temperature_setting = 20

# light 1 related variables
light_1_initialize_flag = 0
light_1_running = 0
light_1_not_running = 0
light_1_start = 0
light_1_off = 0
light_1_time_upload_last = time.time()
light_1_time_upload_now = time.time()
light_1_status = 0

# light 2 related variables
light_2_initialize_flag = 0
light_2_running = 0
light_2_not_running = 0
light_2_start = 0
light_2_off = 0
light_2_time_upload_last = time.time()
light_2_time_upload_now = time.time()
light_2_status = 0

# uploading related variables
baseURL_light_running_1 = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field1=0'
baseURL_light_off_1 = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field2=0'
baseURL_light_running_2 = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field5=0'
baseURL_light_off_2 = 'https://api.thingspeak.com/update?api_key=ZXYPJWBZXNHXGSZB&field6=0'

# panel update rate (ms)
UPDATE_RATE = 500


def uploading_light_running_time():
    global light_1_time_upload_now
    global light_1_time_upload_last
    global light_1_running
    global baseURL_light_running_1
    light_1_time_upload_now = time.time()

    if (light_1_time_upload_now - light_1_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_running_1 + str(light_1_running))
        print(f.content)
        print('uploading succeed')
        light_1_time_upload_last = light_1_time_upload_now
        light_1_running = 0
    else:
        print('not uploading because of the limitation of ThingSpeak')


def uploading_light_running_time_2():
    global light_2_time_upload_now
    global light_2_time_upload_last
    global light_2_running
    global baseURL_light_running_2
    light_2_time_upload_now = time.time()

    if (light_2_time_upload_now - light_2_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_running_2 + str(light_2_running))
        print(f.content)
        print('uploading succeed')
        light_2_time_upload_last = light_2_time_upload_now
        light_2_running = 0
    else:
        print('not uploading because of the limitation of ThingSpeak')


def uploading_light_off_time():
    global light_1_time_upload_now
    global light_1_time_upload_last
    global light_1_not_running
    global baseURL_light_off_1
    light_1_time_upload_now = time.time()
    if (light_1_time_upload_now - light_1_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_off_1 + str(light_1_not_running))
        print(f.content)
        print('uploading succeed')
        light_1_time_upload_last = light_1_time_upload_now
        light_1_not_running = 0
    else:
        print('not uploading because of the limitation of ThingSpeak')


def uploading_light_off_time_2():
    global light_2_time_upload_now
    global light_2_time_upload_last
    global light_2_not_running
    global baseURL_light_off_2
    light_2_time_upload_now = time.time()
    if (light_2_time_upload_now - light_2_time_upload_last) > 15:
        print('uploading')
        f = requests.get(baseURL_light_off_2 + str(light_2_not_running))
        print(f.content)
        print('uploading succeed')
        light_2_time_upload_last = light_2_time_upload_now
        light_2_not_running = 0
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
            GPIO.output(PIN_1, GPIO.HIGH)
        print("light on")
        light_1_status = 1
        panel_status.set(str(light_1_status) + str(light_2_status))
        light_1_start = time.time()
        if light_1_initialize_flag == 0:
            light_1_initialize_flag = 1
            light_1_off = light_1_start
        light_1_not_running += (light_1_start - light_1_off)
        print('light #1\'s total off time is ' + str(round(light_1_not_running)) + ' seconds')
        uploading_light_off_time()


def open_light_2():
    global light_2_start
    global light_2_off
    global light_2_status
    global light_2_not_running
    global light_2_initialize_flag
    if light_2_status == 1:
        print("light #2 is already on, do nothing")
    else:
        if use_device:
            GPIO.output(PIN_2, GPIO.HIGH)
        print("light #2 on")
        light_2_status = 1
        panel_status.set(str(light_1_status) + str(light_2_status))
        light_2_start = time.time()
        if light_2_initialize_flag == 0:
            light_2_initialize_flag = 1
            light_2_off = light_1_start
        light_2_not_running += (light_2_start - light_2_off)
        print('light #2\'s total off time is ' + str(round(light_2_not_running)) + ' seconds')
        uploading_light_off_time_2()


def close_light():
    global light_1_running
    global light_1_start
    global light_1_off
    global light_1_status
    if light_1_status == 0:
        print("light #1 is already closed, do nothing")
    else:
        if use_device:
            GPIO.output(PIN_1, GPIO.LOW)
        print("light #1 off")
        light_1_status = 0
        panel_status.set(str(light_1_status) + str(light_2_status))
        light_1_off = time.time()
        light_1_running += (light_1_off - light_1_start)
        print('light #1\'s total on time is '  + str(round(light_1_running)) + ' seconds')
        uploading_light_running_time()


def close_light_2():
    global light_2_running
    global light_2_start
    global light_2_off
    global light_2_status
    if light_2_status == 0:
        print("light #2 is already closed, do nothing")
    else:
        if use_device:
            GPIO.output(PIN_2, GPIO.LOW)
        print("light #2 off")
        light_2_status = 0
        panel_status.set(str(light_1_status) + str(light_2_status))
        light_2_off = time.time()
        light_2_running += (light_2_off - light_2_start)
        print('light #2\'s total on time is '  + str(round(light_2_running)) + ' seconds')
        uploading_light_running_time_2()


def decode_light(command):
    if command == "00":
        close_light()
    elif command == "01":
        open_light()
    elif command == "10":
        close_light_2()
    elif command == "11":
        open_light_2()
    else:
        print("invalid light instruction")


def decode_ac(command):
    if command == "000":
        print("air-conditioner off")
        temperature_setting.set("Off")
    elif command == "010":
        print("air-conditioner on")
    elif command[0] == "1":
        # current_temperature_setting = int(command[1:3])
        # temperature_setting.set(str(current_temperature_setting) + u'\N{DEGREE SIGN}'+'C')
        temperature_setting.set(str(int(command[1:3])) + u'\N{DEGREE SIGN}' + 'C')
        print("temperature setting is changed to: " + temperature_setting.get())
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
        self.img = Label(self, image=self.render, textvariable=temperature_setting, compound=tk.CENTER)
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
            device type: 1x - lighting system
                         01 - light 1
                         02 - light 2
                         1x - air-conditioner
            000x: light 1 off
            001x: light 2 on
            010x: light 2 off
            011x: light 2 on
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
            if status_tmp == '00':
                self.render = ImageTk.PhotoImage(self.load_1)
            elif status_tmp == '10':
                self.render = ImageTk.PhotoImage(self.load_2)
            elif status_tmp == '01':
                self.render = ImageTk.PhotoImage(self.load_3)
            else:
                self.render = ImageTk.PhotoImage(self.load_4)
            self.img.config(image=self.render)

    def updater(self):
        self.read_instruction()
        self.create_widgets()
        self.after(UPDATE_RATE, self.updater)

    @staticmethod
    def client_exit(self):
        global light_1_status
        global light_1_off
        global light_1_running
        global light_1_not_running
        global light_2_status
        global light_2_off
        global light_2_running
        global light_2_not_running
        if use_device:
            GPIO.output(PIN_1, GPIO.LOW)
            GPIO.output(PIN_2, GPIO.LOW)
            print("light off")
        if light_1_status == 1:
            light_1_status = 0
            light_1_off = time.time()
            light_1_running += (light_1_off - light_1_start)
        else:
            light_1_not_running += (time.time() - light_1_off)
        if light_2_status == 1:
            light_2_status = 0
            light_2_off = time.time()
            light_2_running += (light_2_off - light_2_start)
        else:
            light_2_not_running += (time.time() - light_2_off)
        uploading_light_running_time()
        uploading_light_off_time()
        uploading_light_running_time_2()
        uploading_light_off_time_2()
        exit()


root = tk.Tk()
temperature_setting = StringVar()
temperature_setting.set('Off')
panel_status = StringVar()
panel_status.set('00')
root.title("monitor")
root.geometry("1237x761")
app = Application(root)
root.mainloop()
