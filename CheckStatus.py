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
cursor.execute("DELETE FROM TargetStatus")
conn.commit()  # создаем таблицу, если ее нет

dt = 1

while True:
    try:
        wait_targets = {}  # {id: [x_last, y_last]}
        for value in cursor.execute("SELECT * FROM TargetStatus"):  # find wait targets
            if not value:
                break
            else:
                target_id = value[0]
                x_last = value[1]
                y_last = value[2]
                status = value[3]
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
                        cursor.execute("UPDATE TargetStatus SET status = 'destroyed' WHERE id = (?)", (row[0],))
                        conn.commit()
                        continue
                    else:
                        edit_targets[row[0]] = 'miss'
                        print('Промах по цели {id_}'.format(id_=row[0]))
                        cursor.execute("UPDATE TargetStatus SET status = 'miss' WHERE id = (?)", (row[0],))
                        conn.commit()
                        continue

    except ValueError:
        continue
conn.close()
