#!/usr/bin/env python


import os
import subprocess
import sys
import signal
from time import sleep
from math import sqrt, atan, pi


def get_pid():
    return os.getpid()


def check_point(radius, x, y, percent, start_angle):
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


def calc_speed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


def find_last_file(target_id):
    pwd = subprocess.run(['pwd'], stdout=subprocess.PIPE)
    pwd_string = pwd.stdout.decode('utf-8').rstrip()
    target_dir = pwd_string + '/Files/LastTargets'
    grep_out = subprocess.run(['grep', '-i', target_id, target_dir], stdout=subprocess.PIPE)
    return grep_out.stdout.decode('utf-8').rstrip()[-18:]


class Shooter:
    def __init__(self, name):
        self.name = name
        self.dt = 1
        self.wait_targets = {}  # may be use missed targets
        self.detected_targets = set()
        self.destroyed_targets = set()
        self.fire_mode = True
        self.message_detect_mode = False
        self.num_last_targets = 150
        if name == 'SPRO1':
            self.x = 2500
            self.y = 2500
            self.range = 1700
            self.ammunition = 10
        elif name == 'ZRDN1':
            self.x = 2950
            self.y = 4500
            self.range = 600
            self.ammunition = 20
        elif name == 'ZRDN2':
            self.x = 4400
            self.y = 4100
            self.range = 600
            self.ammunition = 20
        elif name == 'ZRDN3':
            self.x = 5400
            self.y = 3400
            self.range = 600
            self.ammunition = 20
        else:
            print('Unknown object')
            exit(1)

    def check_circle(self, point):
        current_x = point[0] - self.x
        current_y = point[1] - self.y
        percent = 100
        start_angle = 0
        return check_point(self.range, current_x, current_y, percent, start_angle)

    def find_last_targets(self):
        target_list = []
        list_last_files = subprocess.run(['ls', '-t', '/tmp/GenTargets/Targets'], stdout=subprocess.PIPE)
        for line in list_last_files.stdout.decode('utf-8').rstrip().splitlines()[-self.num_last_targets:]:
            data = open('/tmp/GenTargets/Targets/' + line, 'r')
            xy = data.read().splitlines()[0].split(',')
            x = float(xy[0][1:]) / 1000
            y = float(xy[1][1:]) / 1000
            inside = self.check_circle([x, y])
            if inside:
                target_list.append([line[-6:], x, y])  # [id, x, y]
        return target_list

    def check_ammunition(self):
        if self.ammunition == 0 and not self.message_detect_mode:
            self.fire_mode = False
            self.message_detect_mode = True
            out_text = 'Закончился боекомплект, переход в режим обнаружения'
            print(out_text)
            # send socket message to VKO
            return False
        elif not self.fire_mode:
            return False
        else:
            return True

    def speed_condition(self, speed):
        if self.name == 'SPRO1':
            return 8000 <= speed <= 10000
        else:
            return 50 <= speed <= 1000

    def define_and_shoot_targets(self):
        targets = {}  # {id : [prev_xy, last_xy])
        for row in self.find_last_targets():
            id_target = row[0]
            if id_target not in self.destroyed_targets and targets.get(id_target) is None:
                x_prev = row[1]
                y_prev = row[2]
                targets[id_target] = [[x_prev, y_prev]]  # prev_xy
                if id_target not in self.detected_targets:
                    out_text = 'Обнаружена цель ID:{id} с координатами x = {x} y = {y}'.format(id=row[0],
                                                                                               x=x_prev,
                                                                                               y=y_prev)
                    print(out_text)
                    # send socket message to VKO
                    self.detected_targets.add(id_target)
            elif id_target not in self.destroyed_targets and len(targets.get(id_target)) == 1:
                x_last = row[1]
                y_last = row[2]
                targets[id_target].append([x_last, y_last])  # last_xy
                target_data = targets.get(id_target)
                target_speed = calc_speed(target_data[0], target_data[1], self.dt)
                speed_cond = self.speed_condition(target_speed)
                amm_cond = self.check_ammunition()
                if speed_cond and amm_cond and id_target not in self.destroyed_targets:
                    last_file = find_last_file(id_target)
                    self.wait_targets[id_target] = last_file
                    out_text = 'Пуск ракеты по цели {id}'.format(id=id_target)
                    print(out_text)
                    # send socket message to VKO
                    self.ammunition -= 1
                    write_dir = '/tmp/GenTargets/Destroy/' + id_target  # write to tmp/Destroy
                    open(write_dir, 'w+').close()

    def check_targets(self):
        for key, value in list(self.wait_targets.items()):
            new_file = find_last_file(key)
            last_file = value
            if new_file == last_file:
                self.destroyed_targets.add(key)
                out_text = 'Цель {id_} поражена'.format(id_=key)
                print(out_text)
                # send socket message to VKO
                self.wait_targets.pop(key)
            else:
                out_text = 'Промах по цели {id_}'.format(id_=key)
                print(out_text)
                # send socket message to VKO


object_vko = Shooter(sys.argv[1])
pid = get_pid()
while True:
    try:
        object_vko.define_and_shoot_targets()
        sleep(2)
        object_vko.check_targets()
    except KeyboardInterrupt:
        # send socket message to VKO
        os.kill(pid, signal.SIGKILL)
        pass
    except FileNotFoundError:
        continue
