import cv2
import sys
from matplotlib import pyplot as plt
import numpy as np
import os
from os.path import join
width = 640
height = 480
dpp = float((width*height)/10000)



if __name__ == "__main__":
    example = cv2.cvtColor(cv2.imread("training_data/retro_cropped.jpg"), cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(example, 230, 240)
    plt.imshow(canny, 'gray')
    plt.draw()
    plt.waitforbuttonpress()

    _, cont, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    canny = cv2.drawContours(canny, cont, -1, 255, 5)
    plt.imshow(canny, 'gray')
    plt.draw()
    plt.waitforbuttonpress()