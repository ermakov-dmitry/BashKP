#!/usr/bin/env python

import os
import csv
import subprocess
import numpy as np


def create_struct_id_with_coord(filename):
    targets = {}
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in file_reader:
            target_id = row[0]
            target_xy = np.array([int(row[1][1:]), int(row[2][1:])])
            # тут надо выделить дробную часть из координат
            targets[target_id] = target_xy
    return targets


targets_old = create_struct_id_with_coord('Files/TargetsDataOldStep.csv')
targets_cur = create_struct_id_with_coord('Files/TargetsDataCurStep.csv')

for key, value in targets_cur.items():
    print(targets_old.get(key))

# print(os.environ["RLS1_x"])
