from gpiozero import Button
from signal import pause

def say_hello():
    print("Hello!")

button = Button(25)

button.when_pressed = say_hello

pause()
