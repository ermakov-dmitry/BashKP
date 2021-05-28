#!/usr/bin/env python

import csv
from math import sqrt
from time import sleep

open('Files/TargetList.csv', 'w+').close()  # clear data
dt = 1

while True:
    try:
        wait_targets = {}  # {id: [x_last, y_last]}
        with open('Files/TargetList.csv', encoding='utf-8') as r_file:  # find wait targets
            file_reader = csv.reader(r_file, delimiter=",")
            for row in file_reader:
                target_id = row[0]
                x_last = float(row[1])
                y_last = float(row[2])
                status = row[3]
                if status == 'wait':
                    wait_targets[target_id] = [x_last, y_last]
        sleep(5)  # wait new label for targets
        edit_targets = {}  # {id: new_status}
        with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")
            for row in reversed(list(file_reader)):
                if wait_targets.get(row[0]) is not None and edit_targets.get(row[0]) is None:  # если цель еще не встретилась
                    x_new = float(row[1][1:]) / 1000
                    y_new = float(row[2][1:]) / 1000
                    x_last = wait_targets.get(row[0])[0]
                    y_last = wait_targets.get(row[0])[1]
                    if x_new == x_last and y_new == y_last:
                        edit_targets[row[0]] = 'destroyed'
                        print('Цель {id_} поражена'.format(id_=row[0]))  # осталось еще помечать неуничтоженные
                        continue
                    else:
                        edit_targets[row[0]] = 'miss'
                        print('Промах по цели {id_}'.format(id_=row[0]))
                        continue
            with open('Files/TargetList.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                for row in file_reader:

    except ValueError:
        continue
