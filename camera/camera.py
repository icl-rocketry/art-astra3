import picamera
import RPi.GPIO as GPIO

SHORT_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHORT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

with picamera.PiCamera(resolution="1296x972", framerate=40) as camera:
    camera.start_recording('whooosh.h264')
    while not GPIO.input(SHORT_PIN):
        camera.wait_recording(10)
    camera.stop_recording()