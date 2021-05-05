#!/usr/bin/env python


import csv
import os
import numpy as np
import math


def createMapIdWithCoord(filename):
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        targets = {}
        for row in file_reader:
            target_id = row[0]
            target_xy = np.array([float(row[1][1:]) / 1000, float(row[2][1:]) / 1000])
            targets[target_id] = target_xy
    return targets


def checkPoint(radius, x, y, percent, start_angle):
    end_angle = 360 / percent + start_angle
    polar_radius = math.sqrt(x * x + y * y)
    try:
        angle = math.atan(y / x)
    except ZeroDivisionError:
        angle = math.pi / 2
    if angle < 0:
        angle += 2 * math.pi
    if start_angle <= angle <= end_angle and polar_radius < radius:
        return True
    else:
        return False


def checkCollision(a, b, c, x, y, radius):
    dist = ((abs(a * x + b * y + c)) /
            math.sqrt(a * a + b * b))
    if radius == dist:
        print("Touch")
        return False
    elif radius > dist:
        print("Intersect")
        return True
    else:
        print("Outside")
        return False


def checkRLS(point, RLS_x, RLS_y, RLS_alpha, RLS_range, RLS_angle):
    current_x = point[0] - RLS_x
    current_y = point[1] - RLS_y
    percent = (RLS_angle / 360) * 100
    start_angle = np.deg2rad(RLS_alpha - RLS_angle / 2)
    return checkPoint(RLS_range, current_x, current_y, percent, start_angle)


def checkCircle(point, obj_x, obj_y, obj_range):
    current_x = point[0] - obj_x
    current_y = point[1] - obj_y
    percent = 100
    start_angle = 0
    return checkPoint(obj_range, current_x, current_y, percent, start_angle)


targets = createMapIdWithCoord('Files/TargetsDataStep.csv')
RLS1_targets = []
RLS2_targets = []
RLS3_targets = []
ZRDN1_targets = []
ZRDN2_targets = []
ZRDN3_targets = []
SPRO_targets = []


for key, value in targets.items():
    inside = checkRLS(value,
                      float(os.environ["RLS1_x"]),
                      float(os.environ["RLS1_y"]),
                      float(os.environ["RLS1_alpha"]),
                      float(os.environ["RLS1_range"]),
                      float(os.environ["RLS1_angle"]))
    if inside:
        RLS1_targets.append(key)

    inside = checkRLS(value,
                      float(os.environ["RLS2_x"]),
                      float(os.environ["RLS2_y"]),
                      float(os.environ["RLS2_alpha"]),
                      float(os.environ["RLS2_range"]),
                      float(os.environ["RLS2_angle"]))
    if inside:
        RLS2_targets.append(key)

    inside = checkRLS(value,
                      float(os.environ["RLS3_x"]),
                      float(os.environ["RLS3_y"]),
                      float(os.environ["RLS3_alpha"]),
                      float(os.environ["RLS3_range"]),
                      float(os.environ["RLS3_angle"]))
    if inside:
        RLS3_targets.append(key)

    inside = checkCircle(value,
                         float(os.environ["ZRDN1_x"]),
                         float(os.environ["ZRDN1_y"]),
                         float(os.environ["ZRDN1_range"]))
    if inside:
        ZRDN1_targets.append(key)
        continue

    inside = checkCircle(value,
                         float(os.environ["ZRDN2_x"]),
                         float(os.environ["ZRDN2_y"]),
                         float(os.environ["ZRDN2_range"]))
    if inside:
        ZRDN2_targets.append(key)
        continue

    inside = checkCircle(value,
                         float(os.environ["ZRDN3_x"]),
                         float(os.environ["ZRDN3_y"]),
                         float(os.environ["ZRDN3_range"]))
    if inside:
        ZRDN3_targets.append(key)
        continue

    inside = checkCircle(value,
                         float(os.environ["SPRO_x"]),
                         float(os.environ["SPRO_y"]),
                         float(os.environ["SPRO_range"]))
    if inside:
        SPRO_targets.append(key)
        continue

print('--->iter<---')
print(RLS1_targets)
print(RLS2_targets)
print(RLS3_targets)
print(ZRDN1_targets)
print(ZRDN2_targets)
print(ZRDN3_targets)
print(SPRO_targets)
