#!/usr/bin/env python


import os
import sys
import socket
import signal
import subprocess
from datetime import datetime as dtime
from os import remove, path


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
        # print(data.decode('utf-8'))
        conn.send(b'0')
    except KeyboardInterrupt:
        #  here log turn off KP
        bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                       + ' - ' + 'KP' + ': ' + 'Остановлен!' + " >> LogFile.txt"
        subprocess.run(bash_command, shell=True)
        os.kill(os.getpid(), signal.SIGKILL)
