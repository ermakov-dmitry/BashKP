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


def calc_abc(xy1, xy0):
    k = (xy1[1] - xy0[1]) / (xy1[0] - xy0[0])
    yp = k * xy0[0]
    b = xy0[1] - yp
    return -k, 1, -b


def check_collision(a, b, c, x, y, radius):
    dist = ((abs(a * x + b * y + c)) /
            sqrt(a * a + b * b))
    if radius == dist:
        return False
    elif radius > dist:
        return True
    else:
        return False


def calc_speed(xy0, xy1, dt):
    vx = (xy1[0] - xy0[0]) / dt
    vy = (xy1[1] - xy0[1]) / dt
    return sqrt(vx ** 2 + vy ** 2) * 1000  # m/s


class Radar:
    def __init__(self, name):
        self.name = name
        self.dt = 1
        self.ignore_targets = set()
        self.detected_targets = set()
        self.spro_x = 2500
        self.spro_y = 2500
        self.spro_radius = 1700
        self.num_last_targets = 100
        if name == 'Radar1':
            self.x = 3200
            self.y = 3000
            self.alpha = 270
            self.range = 3000
            self.angle = 120
        elif name == 'Radar2':
            self.x = 8000
            self.y = 6000
            self.alpha = 45
            self.range = 7000
            self.angle = 90
        elif name == 'Radar3':
            self.x = 8000
            self.y = 3500
            self.alpha = 270
            self.range = 4000
            self.angle = 200
        else:
            print('Unknown radar')
            exit(1)

    def check_rls(self, point):
        current_x = point[0] - self.x
        current_y = point[1] - self.y
        percent = (self.angle / 360) * 100
        start_angle = (self.alpha - self.angle / 2) * pi / 180
        return check_point(self.range, current_x, current_y, percent, start_angle)

    def find_last_targets(self):
        target_list = []
        list_last_files = subprocess.run(['ls', '-t', '/tmp/GenTargets/Targets'], stdout=subprocess.PIPE)
        for line in list_last_files.stdout.decode('utf-8').rstrip().splitlines()[-self.num_last_targets:]:
            data = open('/tmp/GenTargets/Targets/' + line, 'r')
            xy = data.read().splitlines()[0].split(',')
            x = float(xy[0][1:]) / 1000
            y = float(xy[1][1:]) / 1000
            inside = self.check_rls([x, y])
            if inside:
                target_list.append([line[-6:], x, y])  # [id, x, y]
        return target_list

    def define_targets(self):
        targets = {}  # {id : [prev_xy, last_xy])
        for row in self.find_last_targets():
            id_target = row[0]
            if id_target not in self.ignore_targets and targets.get(id_target) is None:
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
            elif id_target not in self.ignore_targets and len(targets.get(id_target)) == 1:
                x_last = row[1]
                y_last = row[2]
                targets[id_target].append([x_last, y_last])  # last_xy
                target_data = targets.get(id_target)
                target_speed = calc_speed(target_data[0], target_data[1], self.dt)
                if 8000 <= target_speed <= 10000:
                    a, b, c = calc_abc(target_data[0], target_data[1])
                    if check_collision(a, b, c, self.spro_x, self.spro_y, self.spro_radius):
                        out_text = 'Цель ID:{id} движется' \
                                   ' в направлении СПРО, скорость = {v:.3f} м/с'.format(id=row[0],
                                                                                        v=target_speed)
                        print(out_text)
                        # send socket message to VKO
                        self.ignore_targets.add(id_target)


radar = Radar(sys.argv[1])
pid = get_pid()
while True:
    try:
        radar.define_targets()
        sleep(radar.dt)
    except KeyboardInterrupt:
        # send socket message to VKO
        os.kill(pid, signal.SIGKILL)
        pass
    except FileNotFoundError:
        continue
