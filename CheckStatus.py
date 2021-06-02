#!/usr/bin/env python

import csv
from time import sleep
import sqlite3 as sq
import subprocess
from datetime import datetime as dtime

global conn
global cursor


def findLastFile(target_id):
    pwd = subprocess.run(['pwd'], stdout=subprocess.PIPE)
    pwd_string = pwd.stdout.decode('utf-8').rstrip()
    target_dir = pwd_string + '/Files/LastTargets'

    grep_out = subprocess.run(['grep', '-i', target_id, target_dir], stdout=subprocess.PIPE)
    return grep_out.stdout.decode('utf-8').rstrip()[-18:]


conn = sq.connect('Files/TargetList.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS TargetStatus (
                    id TEXT PRIMARY KEY, 
                    last_file TEXT,
                    status TEXT,
                    fire_obj TEXT)""")
cursor.execute("DELETE FROM TargetStatus")
conn.commit()  # создаем таблицу, если ее нет

dt = 5

while True:
    try:
        wait_targets = {}  # {id: [x_last, y_last]}
        edit_targets = {}  # {id: new_status}
        for value in cursor.execute("SELECT * FROM TargetStatus"):  # find wait targets
            if not value:
                break
            else:
                target_id = value[0]
                l_file = value[1]
                status = value[2]
                if status == 'wait':
                    wait_targets[target_id] = l_file
        # sleep(dt)  # wait new label for targets
        with open('Files/TargetsDataStep.csv', encoding='utf-8') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")
            for row in reversed(list(file_reader)):
                if wait_targets.get(row[0]) is not None and edit_targets.get(row[0]) is None:
                    last_file = cursor.execute("SELECT last_file FROM TargetStatus WHERE id = (?)",
                                               (row[0],)).fetchone()[0]
                    conn.commit()
                    sleep(dt)
                    new_file = findLastFile(row[0])
                    print(last_file, '-----------', new_file)
                    if last_file == new_file:
                        fire_obj = cursor.execute("SELECT fire_obj FROM TargetStatus WHERE id = (?)",
                                                  (row[0],)).fetchone()[0]
                        conn.commit()
                        edit_targets[row[0]] = 'destroyed'
                        out_text = 'Цель {id_} поражена'.format(id_=row[0])
                        print(out_text)  # осталось еще помечать неуничтоженные
                        bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                                       + ' --- ' + fire_obj + ': ' + out_text + " >> Files/LogFile.txt"
                        subprocess.run(bash_command, shell=True)
                        cursor.execute("UPDATE TargetStatus SET status = 'destroyed' WHERE id = (?)", (row[0],))
                        conn.commit()
                        continue
                    else:
                        edit_targets[row[0]] = 'miss'
                        out_text = 'Промах по цели {id_}'.format(id_=row[0])
                        print(out_text)
                        bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S")) \
                                       + ': ' + out_text + " >> Files/LogFile.txt"
                        subprocess.run(bash_command, shell=True)
                        cursor.execute("UPDATE TargetStatus SET status = 'miss' WHERE id = (?)", (row[0],))
                        conn.commit()
                        continue
    except ValueError:
        continue
conn.close()
