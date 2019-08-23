from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet


def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0], \
                     detection[2][1], \
                     detection[2][2], \
                     detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0] +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    return img


netMain = None
metaMain = None
altNames = None


class Recognizer:
    def __init__(self, width, height):
        global metaMain, netMain, altNames
        configPath = "/home/algernon/darknet_custom/darknet/cfg/yolo9000.cfg"
        weightPath = "/home/algernon/darknet_custom/darknet/weights/yolo9000.weights"
        metaPath = "/home/algernon/darknet_custom/darknet/cfg/combine9k.data"
        if not os.path.exists(configPath):
            raise ValueError("Invalid config path `" +
                             os.path.abspath(configPath) + "`")
        if not os.path.exists(weightPath):
            raise ValueError("Invalid weight path `" +
                             os.path.abspath(weightPath) + "`")
        if not os.path.exists(metaPath):
            raise ValueError("Invalid data file path `" +
                             os.path.abspath(metaPath) + "`")
        if netMain is None:
            netMain = darknet.load_net_custom(configPath.encode(
                "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
        if metaMain is None:
            metaMain = darknet.load_meta(metaPath.encode("ascii"))
        if altNames is None:
            try:
                with open(metaPath) as metaFH:
                    metaContents = metaFH.read()
                    import re
                    match = re.search("names *= *(.*)$", metaContents,
                                      re.IGNORECASE | re.MULTILINE)
                    if match:
                        result = match.group(1)
                    else:
                        result = None
                    try:
                        if os.path.exists(result):
                            with open(result) as namesFH:
                                namesList = namesFH.read().strip().split("\n")
                                altNames = [x.strip() for x in namesList]
                    except TypeError:
                        pass
            except Exception:
                pass
            self.width = width
            self.height = height
            self.darknet_image = darknet.make_image(self.width, self.height, 3)

    def forward(self, frame):
        #frame_rgb = cv2.cvtColor(frame,  cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame,
                                   (self.width,
                                    self.height),
                                   interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())

        detections = darknet.detect_image(netMain, metaMain, self.darknet_image, thresh=0.15)

        image = cvDrawBoxes(detections, frame_resized)
        # cv2.imshow('ff', image)
        # cv2.waitKey(1)
        return image

