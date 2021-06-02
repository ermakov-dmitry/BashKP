#!/usr/bin/env python


import csv
import os
import math


def createMapIdWithCoord(filename):
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        targets = {}
        for row in file_reader:
            target_id = row[0]
            target_xy = [float(row[1][1:]) / 1000, float(row[2][1:]) / 1000]
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


def checkRLS(point, RLS_x, RLS_y, RLS_alpha, RLS_range, RLS_angle):
    current_x = point[0] - RLS_x
    current_y = point[1] - RLS_y
    percent = (RLS_angle / 360) * 100
    start_angle = (RLS_alpha - RLS_angle / 2) * math.pi / 180
    return checkPoint(RLS_range, current_x, current_y, percent, start_angle)


def checkCircle(point, obj_x, obj_y, obj_range):
    current_x = point[0] - obj_x
    current_y = point[1] - obj_y
    percent = 100
    start_angle = 0
    return checkPoint(obj_range, current_x, current_y, percent, start_angle)


targets = createMapIdWithCoord('Files/TargetsDataStep.csv')

radar1_targets = open('Files/Radar1Targets', 'w')
radar2_targets = open('Files/Radar2Targets', 'w')
radar3_targets = open('Files/Radar3Targets', 'w')
zrdn1_targets = open('Files/ZRDN1Targets', 'w')
zrdn2_targets = open('Files/ZRDN2Targets', 'w')
zrdn3_targets = open('Files/ZRDN3Targets', 'w')
spro_targets = open('Files/SPRO1Targets', 'w')

for key, value in targets.items():
    inside = checkRLS(value,
                      float(os.environ["RLS1_x"]),
                      float(os.environ["RLS1_y"]),
                      float(os.environ["RLS1_alpha"]),
                      float(os.environ["RLS1_range"]),
                      float(os.environ["RLS1_angle"]))
    if inside:
        radar1_targets.write(key + '\n')

    inside = checkRLS(value,
                      float(os.environ["RLS2_x"]),
                      float(os.environ["RLS2_y"]),
                      float(os.environ["RLS2_alpha"]),
                      float(os.environ["RLS2_range"]),
                      float(os.environ["RLS2_angle"]))
    if inside:
        radar2_targets.write(key + '\n')

    inside = checkRLS(value,
                      float(os.environ["RLS3_x"]),
                      float(os.environ["RLS3_y"]),
                      float(os.environ["RLS3_alpha"]),
                      float(os.environ["RLS3_range"]),
                      float(os.environ["RLS3_angle"]))
    if inside:
        radar3_targets.write(key + '\n')

    inside = checkCircle(value,
                         float(os.environ["ZRDN1_x"]),
                         float(os.environ["ZRDN1_y"]),
                         float(os.environ["ZRDN1_range"]))
    if inside:
        zrdn1_targets.write(key + '\n')
        continue

    inside = checkCircle(value,
                         float(os.environ["ZRDN2_x"]),
                         float(os.environ["ZRDN2_y"]),
                         float(os.environ["ZRDN2_range"]))
    if inside:
        zrdn2_targets.write(key + '\n')
        continue

    inside = checkCircle(value,
                         float(os.environ["ZRDN3_x"]),
                         float(os.environ["ZRDN3_y"]),
                         float(os.environ["ZRDN3_range"]))
    if inside:
        zrdn3_targets.write(key + '\n')
        continue

    inside = checkCircle(value,
                         float(os.environ["SPRO_x"]),
                         float(os.environ["SPRO_y"]),
                         float(os.environ["SPRO_range"]))
    if inside:
        spro_targets.write(key + '\n')
        continue


radar1_targets.close()
radar2_targets.close()
radar3_targets.close()
zrdn1_targets.close()
zrdn2_targets.close()
zrdn3_targets.close()
spro_targets.close()
