import cv2
import simplestreamer
import time

streamer = simplestreamer.SimpleStreamer(5800)
streamer.subscribe("10.48.19.20", 5801, "jpg_stream", updates_per_sec=1)

while True:
    time.sleep(0.05)
    jpg_data = streamer.get_data("jpg_stream")
    print(jpg_data)
    if "rgbframe" not in jpg_data:
        continue
    frame = cv2.imdecode(jpg_data["rgbframe"])
    cv2.imshow("frame", frame)