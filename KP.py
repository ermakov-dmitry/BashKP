#!/usr/bin/env python


import os
import socket
import signal


sock = socket.socket()
sock.bind(('', 55000))
sock.listen(100)
while True:
    try:
        conn, address = sock.accept()
        data = conn.recv(1024)
        print(data.decode('utf-8'))
        conn.send(b'0')
    except KeyboardInterrupt:
        #  here log turn off KP
        os.kill(os.getpid(), signal.SIGKILL)
