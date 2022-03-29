import picamera

with picamera.PiCamera(resolution="1296x972", framerate=40) as camera:
    camera.start_recording('video.h264')
    camera.wait_recording(10)
    camera.stop_recording()
