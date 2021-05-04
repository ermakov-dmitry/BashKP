#!/usr/bin/env python

# import os
import csv
# import subprocess
import numpy as np
import math


def createStructIdWithCoord(filename):
    targets = {}
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in file_reader:
            target_id = row[0]
            target_xy = np.array([float(row[1][1:]) / 1000, float(row[2][1:]) / 1000])
            targets[target_id] = target_xy
    return targets


def checkPoint(radius, x, y, percent, startAngle):
    # calculate endAngle
    endAngle = 360 / percent + startAngle

    # Calculate polar co-ordinates
    polarradius = math.sqrt(x * x + y * y)
    Angle = math.atan(y / x)

    # Check whether polarradius is less
    # then radius of circle or not and
    # Angle is between startAngle and
    # endAngle or not
    if startAngle <= Angle <= endAngle and polarradius < radius:
        print("Point (", x, ",", y, ") "
                                    "exist in the circle sector")
        return True
    else:
        print("Point (", x, ",", y, ") "
                                    "does not exist in the circle sector")
        return False


def checkCollision(a, b, c, x, y, radius):
    # Finding the distance of line
    # from center.
    dist = ((abs(a * x + b * y + c)) /
            math.sqrt(a * a + b * b))

    # Checking if the distance is less
    # than, greater than or equal to radius.
    if (radius == dist):
        print("Touch")
    elif (radius > dist):
        print("Intersect")
    else:
        print("Outside")


def checkRLS(point, RLS_x, RLS_y, RLS_alpha, RLS_range, RLS_angle):
    current_x = point[0] - RLS_x
    current_y = point[1] - RLS_y
    percent = RLS_angle / 360
    start_angle = RLS_alpha - RLS_range / 2
    return checkPoint(RLS_range, current_x, current_y, percent, start_angle)


targets_old = createStructIdWithCoord('Files/TargetsDataOldStep.csv')
targets_cur = createStructIdWithCoord('Files/TargetsDataCurStep.csv')

for key, value in targets_old.items():
    cur_xy = targets_cur.get(key)
    #print(value, '-', cur_xy)

    # check RLS1

# need black list points

# print(os.environ["RLS1_x"])
