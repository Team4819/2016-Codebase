import cv2
import pyfreenect2
import time
import csv
import numpy as np
import struct
from networktables import NetworkTable
from os import path
import os

# Init networktables
NetworkTable.setIPAddress("roborio-4819.local")
NetworkTable.setClientMode()
NetworkTable.initialize()

sd = NetworkTable.getTable("SmartDashboard")


# Initialize device
serialNumber = pyfreenect2.getDefaultDeviceSerialNumber()
kinect = pyfreenect2.Freenect2Device(serialNumber, "cpu")

# Set up frame listener
frameListener = pyfreenect2.SyncMultiFrameListener(pyfreenect2.Frame.COLOR,
    pyfreenect2.Frame.DEPTH)

kinect.setColorFrameListener(frameListener)
kinect.setIrAndDepthFrameListener(frameListener)

# Start recording
kinect.start()

dataset = 0
while True:
    dataset_path = "set_{}".format(dataset)
    if not path.exists(dataset_path):
        os.makedirs(dataset_path)
        os.chdir(dataset_path)
        break
    dataset += 1
csv_file = open("posdata.csv", "w")
csv_writer = csv.DictWriter(csv_file, ["frame", "x", "y", "r"])
csv_writer.writeheader()

depth_buffer = np.zeros((424, 512, 1))

time.sleep(1)

# Main loop
frame = 0
while True:
    print("Frame {}".format(frame))
    frame += 1
    frames = frameListener.waitForNewFrame()
    rgbFrame = frames.getFrame(pyfreenect2.Frame.COLOR)
    cv2.imwrite("rgb_{}.jpg".format(frame), rgbFrame.getRGBData()[:, :, [2, 1, 0]])


    depthFrame = frames.getFrame(pyfreenect2.Frame.DEPTH)
    depth_data = depthFrame.getDepthData()
    for x in range(512):
        for y in range(424):
            value = struct.unpack('f', struct.pack('4B', *depth_data[y, x]))[0]
            depth_buffer[y, x, 0] = (4500 - value)/4500*255
    cv2.imwrite("depth_{}.jpg".format(frame), depth_buffer)

    r_pos = sd.getDouble("sensor_input_r_pos", 0)
    x_pos = sd.getDouble("sensor_input_x_pos", 0)
    y_pos = sd.getDouble("sensor_input_y_pos", 0)

    csv_writer.writerow({"frame": frame, "x": x_pos, "y": y_pos, "r": r_pos})

    time.sleep(.20)

csv_file.close()
kinect.stop()
