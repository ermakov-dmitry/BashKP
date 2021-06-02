#!/bin/bash

pid_=$(ps -ef | awk "/python3 $1 $2/{print \$2}" | head -n 1)
kill -9 $pid_
python3 KillMessage.py $2
echo $2 отключен!