import cv2
import pyfreenect2
import simplestreamer
import numpy as np
import struct

# Initialize device
serialNumber = pyfreenect2.getDefaultDeviceSerialNumber()
kinect = pyfreenect2.Freenect2Device(serialNumber, "cuda")

# Set up frame listener
frameListener = pyfreenect2.SyncMultiFrameListener(pyfreenect2.Frame.COLOR,
    pyfreenect2.Frame.DEPTH)

kinect.setColorFrameListener(frameListener)
kinect.setIrAndDepthFrameListener(frameListener)

# Start recording
kinect.start()

depth_streamer = simplestreamer.SimpleStreamer(5800)
jpg_streamer = simplestreamer.SimpleStreamer(5801)

depth_buffer = np.zeros((424, 512, 1))

# Main loop
frame = 0
while True:
    frames = frameListener.waitForNewFrame()

    rgbFrame = frames.getFrame(pyfreenect2.Frame.COLOR)
    cv2mat = cv2.imencode(".jpeg", rgbFrame.getRGBData())
    jpg_streamer.send_data({"rgbframe": cv2mat})

    depthFrame = frames.getFrame(pyfreenect2.Frame.DEPTH)
    depth_data = depthFrame.getDepthData()
    for x in range(512):
        for y in range(424):
            value = struct.unpack('f', struct.pack('4B', *depth_data[y, x]))[0]
            depth_buffer[y, x, 0] = (4500 - value)/4500*255
    depth_streamer.send_data({"rgbframe": depth_buffer})

kinect.stop()
