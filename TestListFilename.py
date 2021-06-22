#!/usr/bin/env python

import subprocess

target_list = []
n_targets = 20
list_last_files = subprocess.run(['ls', '-t', '/tmp/GenTargets/Targets'], stdout=subprocess.PIPE)
for line in list_last_files.stdout.decode('utf-8').rstrip().splitlines()[-n_targets:]:  # and reversed(obj)
    data = open('/tmp/GenTargets/Targets/' + line, 'r')
    xy = data.read().splitlines()[0].split(',')
    target_list.append([line[-6:], float(xy[0][1:]) / 1000, float(xy[1][1:]) / 1000])  # [id, x, y]


print(target_list)
