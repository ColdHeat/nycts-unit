from gpiozero import Button
from signal import pause
import os

def hello_darkness_my_old_friend():
    os.system("sudo pkill -f python")
    os.system("sudo pkill -f node")
    os.system("sudo rm /etc/wpa_supplicant/wpa_supplicant.conf")
    os.system("sudo reboot")

button = Button(25)

button.when_pressed = hello_darkness_my_old_friend

pause()
