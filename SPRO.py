#!/usr/bin/env python

import csv
from math import sqrt
from time import sleep
import sqlite3 as sq

global conn
global cursor

conn = sq.connect('Files/TargetList.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS TargetStatus (
                    id TEXT PRIMARY KEY, 
                    x REAL,
                    y REAL,
                    status MESSAGE_TEXT)""")
conn.commit()  # создаем таблицу, если ее нет


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


def isWaitOrDestroyed(id_):
    status_ = ''
    for value in cursor.execute("SELECT * FROM TargetStatus"):
        if not value:
            break
        status_ = value[3]
        if value[0] == id_ and (status_ == 'wait' or status_ == 'destroyed'):
            return True, status_
    return False, status_


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
                        is_wod, target_status = isWaitOrDestroyed(row[0])
                        if 8000 <= target_speed <= 10000 and not is_wod and fire_mode:
                            id_ = str(row[0])
                            x_l = str(target_data[0][0])
                            y_l = str(target_data[0][1])
                            status = 'wait'
                            data = id_, x_l, y_l, status
                            if target_status == 'miss':
                                cursor.execute("UPDATE TargetStatus SET status = 'wait' WHERE id = (?)", (id_,))
                            else:
                                cursor.execute("INSERT INTO TargetStatus VALUES (?, ?, ?, ?)", data)
                            conn.commit()
                            print('Пуск ракеты по цели {id}'.format(id=id_))
                            ammunition -= 1
                            write_dir = '/tmp/GenTargets/Destroy/' + id_  # write to tmp/Destroy
                            open(write_dir, 'w+').close()

        sleep(dt)
    except ValueError:
        continue
conn.close()
