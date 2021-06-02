#!/usr/bin/env python

import csv
from math import sqrt
from time import sleep
import sqlite3 as sq
import sys
import subprocess
from datetime import datetime as dtime

global conn
global cursor

conn = sq.connect('Files/TargetList.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS TargetStatus (
                    id TEXT PRIMARY KEY, 
                    last_file TEXT,
                    status TEXT,
                    fire_obj TEXT)""")
conn.commit()  # создаем таблицу, если ее нет


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


def isWaitOrDestroyed(id_):
    status_ = 'empty'
    for value in cursor.execute("SELECT * FROM TargetStatus"):
        if not value:
            break
        status_ = value[2]
        if value[0] == id_ and (status_ == 'wait' or status_ == 'destroyed' or status_ == 'miss'):
            return True, status_
    return False, status_


def findLastFile(target_id):
    pwd = subprocess.run(['pwd'], stdout=subprocess.PIPE)
    pwd_string = pwd.stdout.decode('utf-8').rstrip()
    target_dir = pwd_string + '/Files/LastTargets'

    grep_out = subprocess.run(['grep', '-i', target_id, target_dir], stdout=subprocess.PIPE)
    return grep_out.stdout.decode('utf-8').rstrip()[-18:]


ammunition = 20
dt = 1
spro_targets = set()
detected_targets = set()
filename = 'Files/' + sys.argv[1] + 'Targets'
system_type = sys.argv[1]  # [6:11]
if system_type == 'SPRO1':
    ammunition = 10
fire_mode = True
message_detect_mode = False
bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                                           + ' --- ' + sys.argv[1] + ': ' + 'Запущен!' + " >> Files/LogFile.txt"
subprocess.run(bash_command, shell=True)

while True:
    try:
        if ammunition == 0 and not message_detect_mode:
            fire_mode = False
            message_detect_mode = True
            out_text = 'Закончился боекомплект, переход в режим обнаружения'
            print(out_text)
            bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                           + ' --- ' + sys.argv[1][6:11] + ': ' + out_text + " >> Files/LogFile.txt"
            subprocess.run(bash_command, shell=True)
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
                            out_text = 'Обнаружена цель ID:{id} с координатами x = {x} y = {y}'.format(id=row[0],
                                                                                                       x=x_last,
                                                                                                       y=y_last)
                            print(out_text)
                            bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                                           + ' --- ' + sys.argv[1] + ': ' + out_text + " >> Files/LogFile.txt"
                            subprocess.run(bash_command, shell=True)
                            detected_targets.add(row[0])
                    elif len(targets_coord.get(row[0])) == 1:
                        x_prev = float(row[1][1:]) / 1000
                        y_prev = float(row[2][1:]) / 1000
                        targets_coord[row[0]].append([x_prev, y_prev])
                        target_data = targets_coord.get(row[0])  # добавляем список списков с данными по цели
                        target_speed = calcSpeed(target_data[1], target_data[0], dt)
                        is_wod, target_status = isWaitOrDestroyed(row[0])
                        speed_condition = 50 <= target_speed <= 1000
                        if system_type == 'SPRO1':
                            speed_condition = 8000 <= target_speed <= 10000
                        if speed_condition and not is_wod and fire_mode:
                            id_ = str(row[0])
                            last_file = findLastFile(id_)
                            status = 'wait'
                            data = id_, last_file, status, sys.argv[1]
                            cursor.execute("INSERT INTO TargetStatus VALUES (?, ?, ?, ?)", data)
                            conn.commit()
                            out_text = 'Пуск ракеты по цели {id}'.format(id=id_)
                            print(out_text)  #
                            bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                                           + ' --- ' + sys.argv[1] + ': ' + out_text + " >> Files/LogFile.txt"
                            subprocess.run(bash_command, shell=True)
                            ammunition -= 1  # этот блок можно вынести за условие, но как поведет себя
                            write_dir = '/tmp/GenTargets/Destroy/' + id_  # write to tmp/Destroy
                            open(write_dir, 'w+').close()  # гентаргетс при перезаписи промаха неизвестно

        sleep(dt)
    except ValueError:
        continue
conn.close()