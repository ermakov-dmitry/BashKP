#!/usr/bin/env python


import csv
import os
import math


def calcAbc(xy1, xy0):
    k = (xy1[1] - xy0[1]) / (xy1[0] - xy0[0])
    yp = k * xy0[0]
    b = xy0[1] - yp
    return -k, 1, -b


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


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return math.sqrt(vx**2 + vy**2) * 1000  # m/s


dt = 1  # float(os.environ["delta_t"])
radar_targets = set()
ignore_targets = set()
found_collision_targets = set()
spro_x = 2500
spro_y = 2500
spro_radius = 1700

filename = 'Files/Radar3Targets'

while True:
    f = open(filename)
    for line in f:
        radar_targets.add(line[:6])

    targets_coord = {}  # {id : [last_xy, prev_xy])
    xy_last = [-1, -1]
    xy_prev = [-1, -1]
    with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in reversed(list(file_reader)):
            if row[0] in radar_targets and row[0] not in ignore_targets and row[0] not in found_collision_targets:
                if targets_coord.get(row[0]) is None:
                    targets_coord[row[0]] = [[float(row[1][1:]) / 1000, float(row[2][1:]) / 1000]]
                elif len(targets_coord.get(row[0])) == 1:
                    targets_coord[row[0]].append([float(row[1][1:]) / 1000, float(row[2][1:]) / 1000])
                else:
                    target_data = targets_coord.get(row[0])
                    target_speed = calcSpeed(target_data[1], target_data[0], dt)
                    if 8000 <= target_speed <= 10000:
                        a, b, c = calcAbc(target_data[1], target_data[0])
                        if checkCollision(a, b, c, spro_x, spro_y, spro_radius):
                            print('Цель в летит в зону СПРО!')
                            ignore_targets.add(row[0])
                            found_collision_targets.add(row[0])
