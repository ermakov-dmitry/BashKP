#!/usr/bin/env python


import os
import sys
import ctypes
import socket
import signal
import subprocess
from platform import system
from datetime import datetime as dtime
from os import remove, path


def is_admin():
    try:
        is_adm = (os.getuid() == 0)
    except AttributeError:
        is_adm = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_adm


if is_admin() or system() != 'Linux':
    print('Ошибка! Запуск с ОС, отличной от Linux, или запуск с правами администратора.')
    exit(1)
sock = socket.socket()
sock.bind(('', 55000))
sock.listen(100)
kp = sys.argv[1]
if path.exists("LogFile.txt"):
    remove("LogFile.txt")
bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                       + ' - ' + kp + ': ' + 'Запущен!' + " >> LogFile.txt"
subprocess.run(bash_command, shell=True)
while True:
    try:
        conn, address = sock.accept()
        data = conn.recv(1024)
        subprocess.run('echo ' + data.decode('utf-8') + ' >> LogFile.txt', shell=True)
        conn.send(b'0')
    except KeyboardInterrupt:
        bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                       + ' - ' + 'KP' + ': ' + 'Остановлен!' + " >> LogFile.txt"
        subprocess.run(bash_command, shell=True)
        os.kill(os.getpid(), signal.SIGKILL)
