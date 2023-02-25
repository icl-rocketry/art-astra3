import time
import board
import pwmio

# define pins
servo = pwmio.PWMOut(board.GP3, duty_cycle=0, frequency=330, variable_frequency=False)

def move(position):
    print("Started movement")
    servo.duty_cycle = (65535 * position) // 100
    time.sleep(0.5)
    print("Ended movement")

while True:
    try:
        position = int(input("Enter position: "))
        move(position)
    except ValueError:
        print("Invalid input - range is 0 to 100")
    time.sleep(1)