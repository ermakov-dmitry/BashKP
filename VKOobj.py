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
            try:
                target_id = row[0]
                target_xy = [float(row[1][1:]) / 1000, float(row[2][1:]) / 1000]
                targets[target_id] = target_xy
            except IndexError:
                continue
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


def checkCircle(point, obj_x, obj_y, obj_range):
    current_x = point[0] - obj_x
    current_y = point[1] - obj_y
    percent = 100
    start_angle = 0
    return checkPoint(obj_range, current_x, current_y, percent, start_angle)


def calcSpeed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


def isWaitOrDestroyed(id_, target_list):
    status_ = 'empty'
    for key, value in target_list.items():
        if target_list == {}:
            break
        status_ = value[0]
        if key == id_ and (status_ == 'wait' or status_ == 'destroyed'):  # or miss
            return True, status_
        elif key == id_ and status_ == 'miss':
            return False, status_
    return False, status_


def findLastFile(target_id):
    pwd = subprocess.run(['pwd'], stdout=subprocess.PIPE)
    pwd_string = pwd.stdout.decode('utf-8').rstrip()
    target_dir = pwd_string + '/Files/LastTargets'
    grep_out = subprocess.run(['grep', '-i', target_id, target_dir], stdout=subprocess.PIPE)
    return grep_out.stdout.decode('utf-8').rstrip()[-18:]


ammunition = 20
dt = 1
obj_targets = set()
detected_targets = set()
destroyed_targets = set()
status_of_targets = {}  # {id: [status, last_file]}
filename = 'Files/' + sys.argv[1] + 'Targets'
system_type = sys.argv[1]  # [6:11]
if system_type == 'SPRO1':
    ammunition = 10
fire_mode = True
message_detect_mode = False
bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                                           + ' --- ' + sys.argv[1] + ': ' + 'Запущен!' + " >> Files/LogFile.txt"
subprocess.run(bash_command, shell=True)
obj_x = 2500
obj_y = 2500
obj_range = 1700
if system_type == 'SPRO1':
    obj_x = 2500
    obj_y = 2500
    obj_range = 1700
elif system_type == 'ZRDN1':
    obj_x = 2950
    obj_y = 4500
    obj_range = 600
elif system_type == 'ZRDN2':
    obj_x = 4400
    obj_y = 4100
    obj_range = 600
elif system_type == 'ZRDN3':
    obj_x = 5400
    obj_y = 3400
    obj_range = 600
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
        targets = createMapIdWithCoord('Files/TargetsDataStep.csv')
        for key, value in targets.items():
            inside = checkCircle(value, obj_x, obj_y, obj_range)
            if inside:
                obj_targets.add(key)
        targets_coord = {}  # {id : [last_xy, prev_xy])
        with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")
            for row in reversed(list(file_reader)):
                if row[0] in obj_targets:
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
                        is_wod, target_status = isWaitOrDestroyed(row[0], status_of_targets)
                        speed_condition = 50 <= target_speed <= 1000
                        if system_type == 'SPRO1':
                            speed_condition = 8000 <= target_speed <= 10000
                        if speed_condition and not is_wod and fire_mode:
                            id_ = row[0]
                            last_file = findLastFile(id_)
                            status = 'wait'
                            status_of_targets[id_] = [status, last_file]
                            out_text = 'Пуск ракеты по цели {id}'.format(id=id_)
                            print(out_text)  #
                            bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                                           + ' --- ' + sys.argv[1] + ': ' + out_text + " >> Files/LogFile.txt"
                            subprocess.run(bash_command, shell=True)
                            ammunition -= 1  # этот блок можно вынести за условие, но как поведет себя
                            write_dir = '/tmp/GenTargets/Destroy/' + id_  # write to tmp/Destroy
                            open(write_dir, 'w+').close()  # гентаргетс при перезаписи промаха неизвестно

        sleep(dt + 3)  # после идет проверка на попадание

        for key, value in status_of_targets.items():
            new_file = findLastFile(key)
            last_file = value[1]
            if new_file == last_file and key not in destroyed_targets:
                destroyed_targets.add(key)
                out_text = 'Цель {id_} поражена'.format(id_=key)
                status_of_targets[key] = ['destroyed', new_file]
                print(out_text)
                bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                               + ' --- ' + system_type + ': ' + out_text + " >> Files/LogFile.txt"
                subprocess.run(bash_command, shell=True)
            elif new_file != last_file and key not in destroyed_targets:
                out_text = 'Промах по цели {id_}'.format(id_=row[0])
                status_of_targets[key] = ['miss', new_file]
                print(out_text)
                bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                               + ' --- ' + system_type + ': ' + out_text + " >> Files/LogFile.txt"
                subprocess.run(bash_command, shell=True)
    except ValueError:
        continue
