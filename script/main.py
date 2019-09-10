#!/usr/bin/env python
import rospy 
import rospkg
import csv
import matplotlib.pyplot as plt
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import Point
from tbtop_square.msg import Projected
from math import *
import numpy as np
from scipy import stats
from scipy import optimize
import time

from detect_square import detect_rect
import cv2

class MyQueue:
    def __init__(self, N):
        self.N = N
        self.data = [np.zeros(3) for n in range(N)]

    def push(self, elem):
        tmp = self.data[1:self.N]
        tmp.append(elem)
        self.data = tmp

    def mean(self):
        s_est_lst = [np.mean(np.array([s[i] for s in self.data])) for i in range(3)]
        return np.array(s_est_lst)

class SquareDetector:
    def __init__(self, n_ave = 10):
        self.sub = rospy.Subscriber("input", Projected, self.callback)
        self.pub = rospy.Publisher("output", Point, queue_size = 10)
        self.s_queue = MyQueue(n_ave)

    def callback(self, msg):
        x1 = np.array(msg.x_array.data)
        x2 = np.array(msg.y_array.data)
        x = np.vstack((x1, x2))
        s_est_, size = detect_rect(x)

        isInvalid =  size < 0.005 ** 2
        if not isInvalid:
            self.s_queue.push(s_est_)

        s_est = self.s_queue.mean()
        print s_est
        s_est = Point(x = s_est_[0], y = s_est_[1], z = s_est_[2])
        self.pub.publish(s_est)


if __name__=='__main__':
    rospy.init_node("detect_square", anonymous = True)
    sd = SquareDetector()
    rospy.spin()





