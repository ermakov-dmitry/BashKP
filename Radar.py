#!/usr/bin/env python


import csv
from math import sqrt, pi, atan
from time import sleep
import sys
import subprocess
from datetime import datetime as dtime


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
    polar_radius = sqrt(x * x + y * y)
    try:
        angle = atan(y / x)
    except ZeroDivisionError:
        angle = pi / 2
    if angle < 0:
        angle += 2 * pi
    if start_angle <= angle <= end_angle and polar_radius < radius:
        return True
    else:
        return False


def checkRLS(point, RLS_x, RLS_y, RLS_alpha, RLS_range, RLS_angle):
    current_x = point[0] - RLS_x
    current_y = point[1] - RLS_y
    percent = (RLS_angle / 360) * 100
    start_angle = (RLS_alpha - RLS_angle / 2) * pi / 180
    return checkPoint(RLS_range, current_x, current_y, percent, start_angle)


def calcAbc(xy1, xy0):
    k = (xy1[1] - xy0[1]) / (xy1[0] - xy0[0])
    yp = k * xy0[0]
    b = xy0[1] - yp
    return -k, 1, -b


def checkCollision(a, b, c, x, y, radius):
    dist = ((abs(a * x + b * y + c)) /
            sqrt(a * a + b * b))
    if radius == dist:
        return False
    elif radius > dist:
        return True
    else:
        return False


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


dt = 1
radar_targets = set()
ignore_targets = set()
detected_targets = set()
spro_x = 2500
spro_y = 2500
spro_radius = 1700
filename = 'Files/' + sys.argv[1] + 'Targets'
bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                                           + ' --- ' + sys.argv[1] + ': ' + 'Запущен!' + " >> Files/LogFile.txt"
subprocess.run(bash_command, shell=True)
RLS_x = 0
RLS_y = 0
RLS_alpha = 0
RLS_range = 0
RLS_angle = 0
if sys.argv[1] == 'Radar1':
    RLS_x = 3200
    RLS_y = 3000
    RLS_alpha = 270
    RLS_range = 3000
    RLS_angle = 120
elif sys.argv[1] == 'Radar2':
    RLS_x = 8000
    RLS_y = 6000
    RLS_alpha = 45
    RLS_range = 7000
    RLS_angle = 90
elif sys.argv[1] == 'Radar3':
    RLS_x = 8000
    RLS_y = 3500
    RLS_alpha = 270
    RLS_range = 4000
    RLS_angle = 200

while True:
    try:
        targets = createMapIdWithCoord('Files/TargetsDataStep.csv')
        for key, value in targets.items():
            inside = checkRLS(value, RLS_x, RLS_y, RLS_alpha, RLS_range, RLS_angle)
            if inside:
                radar_targets.add(key)
        targets_coord = {}  # {id : [last_xy, prev_xy])
        with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")
            for row in reversed(list(file_reader)):
                if row[0] in radar_targets and row[0] not in ignore_targets:  # если id в
                    if targets_coord.get(row[0]) is None:
                        x_last = float(row[1][1:]) / 1000
                        y_last = float(row[2][1:]) / 1000
                        targets_coord[row[0]] = [[x_last, y_last]]
                        if row[0] not in detected_targets:
                            out_text = 'Обнаружена цель ID:{id} с координатами x = {x} y = {y}'.format(id=row[0],
                                                                                                       x=x_last,
                                                                                                       y=y_last)
                            print(out_text)
                            bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                                           + ' --- ' + sys.argv[1] + ': ' + out_text + " >> Files/LogFile.txt"
                            subprocess.run(bash_command, shell=True)
                            detected_targets.add(row[0])
                    elif len(targets_coord.get(row[0])) == 1:
                        x_prev = float(row[1][1:]) / 1000
                        y_prev = float(row[2][1:]) / 1000
                        targets_coord[row[0]].append([x_prev, y_prev])
                        target_data = targets_coord.get(row[0])  # добавляем список списков с данными по цели
                        target_speed = calcSpeed(target_data[1], target_data[0], dt)
                        if 8000 <= target_speed <= 10000:
                            a, b, c = calcAbc(target_data[1], target_data[0])
                            if checkCollision(a, b, c, spro_x, spro_y, spro_radius):
                                out_text = 'Цель ID:{id} движется' \
                                           ' в направлении СПРО, скорость = {v:.3f} м/с'.format(id=row[0],
                                                                                                v=target_speed)
                                print(out_text)
                                bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                                               + ' --- ' + sys.argv[1] + ': ' + out_text + " >> Files/LogFile.txt"
                                subprocess.run(bash_command, shell=True)
                        ignore_targets.add(row[0])

        sleep(dt)
    except ValueError:
        continue
