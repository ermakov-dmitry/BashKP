#!/usr/bin/env python


import sys
import subprocess
from datetime import datetime as dtime

bash_command = "echo " + str(dtime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                       + ' - ' + sys.argv[1] + ': ' + 'Остановлен!' + " >> LogFile.txt"
subprocess.run(bash_command, shell=True)
