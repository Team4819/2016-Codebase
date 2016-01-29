import cv2
import sys
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import os
from shutil import copyfile
from os.path import join
width = 640
height = 480
dpp = float((width*height)/10000)
font = cv2.FONT_HERSHEY_PLAIN

fig = plt.figure()
last_key = None


def onkey(event):
    global last_key
    last_key = event.key
fig.canvas.mpl_connect('key_press_event', onkey)

def find_goals(img, disp_part=False):
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)
    if disp_part:
        plt.imshow(edges, 'gray')
        plt.draw()
        plt.waitforbuttonpress()
    _, contours, hierarcy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    goals = []
    for h, cont in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cont)
        aspect = h/w
        if h*w/dpp > 50 and abs(aspect-0.5) < 1:
            #cv2.drawContours(img, [cont], 0, (0, 255, 0), 5)
            goals.append((int(x+w/2), int(y+h/2), "Goal!"))
    return goals


def highlight_image(filename):
    global last_key
    orig = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)
    goals = find_goals(orig, False)
    if len(goals) > 1:
        return "n"
    for x, y, msg in goals:
        cv2.circle(orig, (x, y), 2, (255, 0, 0), -1)
        cv2.putText(orig, msg, (x, y), font, 1, (0, 255, 255))
    cv2.putText(orig, "Found {} goal(s)".format(len(goals)), (int(width/2), height-20), font, 1, (255, 255, 255))
    plt.imshow(orig)
    last_key = None
    plt.draw()
    while last_key is None:
        plt.waitforbuttonpress()
    return last_key

if __name__ == "__main__":
    for file in sorted(os.listdir(sys.argv[1])):
        if file.endswith(".jpg"):
            fname = join(sys.argv[1], file)
            response = highlight_image(fname)
            if len(sys.argv) > 2:
                if response == "y":
                    print("Saving!")
                    copyfile(fname, join(sys.argv[2], file))
                else:
                    print("not saving....")


