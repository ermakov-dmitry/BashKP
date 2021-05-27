#!/usr/bin/env python


import csv
from math import sqrt
from time import sleep


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


dt = 1  # float(os.environ["delta_t"])
radar_targets = set()
ignore_targets = set()
detected_targets = set()
spro_x = 2500
spro_y = 2500
spro_radius = 1700
filename = 'Files/Radar1Targets'

while True:
    try:
        f = open(filename)
        for line in f:
            radar_targets.add(line[:6])  # добавляем в множество цели нужной РЛС

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
                            print('Обнаружена цель ID:{id} с координатами x = {x} y = {y}'
                                  .format(id=row[0], x=x_last, y=y_last))
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
                                print('Цель ID:{id} движется в направлении СПРО, скорость = {v:.3f} м/с'
                                      .format(id=row[0], v=target_speed))
                        ignore_targets.add(row[0])

        sleep(dt)
    except ValueError:
        continue
