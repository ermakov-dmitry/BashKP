#!/usr/bin/env python

import csv
from math import sqrt
from time import sleep
import sqlite3 as sq

global conn
global cursor

conn = sq.connect('TargetList.db')
cursor = conn.cursor()


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


def isWaitOrDestroyed(filename, id):
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in file_reader:
            if not row:
                break
            if row[0] == id and (row[3] == 'wait' or row[3] == 'destroyed'):
                return True
        return False


ammunition = 10
dt = 1
spro_targets = set()
detected_targets = set()
filename = 'Files/SPROTargets'
fire_mode = True
message_detect_mode = False

while True:
    try:
        if ammunition == 0 and not message_detect_mode:
            fire_mode = False
            message_detect_mode = True
            print('СПРО: закончился боекомплект, переход в режим обнаружения')
        f = open(filename)
        for line in f:
            spro_targets.add(line[:6])  # добавляем в множество цели нужной РЛС
        targets_coord = {}  # {id : [last_xy, prev_xy])
        with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")
            for row in reversed(list(file_reader)):
                if row[0] in spro_targets:
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
                        if 8000 <= target_speed <= 10000 and not isWaitOrDestroyed('Files/TargetList.csv', row[0]) and fire_mode:
                            with open('Files/TargetList.csv', 'a') as fd:
                                id_ = str(row[0])
                                x_l = str(target_data[0][0])
                                y_l = str(target_data[0][1])
                                status = 'wait'
                                fd.write(id_ + ',' + x_l + ',' + y_l + ',' + status + '\n')
                                print('Пуск ракеты по цели {id}'.format(id=id_))
                                ammunition -= 1
                                write_dir = '/tmp/GenTargets/Destroy/' + id_  # write to tmp/Destroy
                                open(write_dir, 'w+').close()

        sleep(dt)
    except ValueError:
        continue
