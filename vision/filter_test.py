import cv2
import sys
from matplotlib import pyplot as plt
import numpy as np
import os
from os.path import join
width = 640
height = 480
dpp = float((width*height)/10000)
font = cv2.FONT_HERSHEY_PLAIN

def find_goals(img, disp_part=False):
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY), 150, 200)
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
            cv2.drawContours(img, [cont], 0, (0, 255, 0), 5)
            goals.append((int(x+w/2), int(y+h/2), "Goal!"))
    return goals


def highlight_image(filename):
    orig = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)
    goals = find_goals(orig, True)
    for x, y, msg in goals:
        cv2.circle(orig, (x, y), 2, (255, 0, 0), -1)
        cv2.putText(orig, msg, (x, y), font, 1, (0, 255, 255))
    cv2.putText(orig, "Found {} goal(s)".format(len(goals)), (int(width/2), height-20), font, 1, (255, 255, 255))
    plt.imshow(orig)
    plt.draw()
    plt.waitforbuttonpress()

if __name__ == "__main__":
    for file in os.listdir(sys.argv[1]):
        if file.endswith(".jpg"):
            highlight_image(join(sys.argv[1], file))
