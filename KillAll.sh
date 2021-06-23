#!/bin/bash

Radar1_=$(ps -ef | awk "/python3 Radar.py Radar1/{print \$2}" | head -n 1)
Radar2_=$(ps -ef | awk "/python3 Radar.py Radar2/{print \$2}" | head -n 1)
Radar3_=$(ps -ef | awk "/python3 Radar.py Radar3/{print \$2}" | head -n 1)
ZRDN1_=$(ps -ef | awk "/python3 ShootObject.py ZRDN1/{print \$2}" | head -n 1)
ZRDN2_=$(ps -ef | awk "/python3 ShootObject.py ZRDN2/{print \$2}" | head -n 1)
ZRDN3_=$(ps -ef | awk "/python3 ShootObject.py ZRDN3/{print \$2}" | head -n 1)
SPRO1_=$(ps -ef | awk "/python3 ShootObject.py SPRO1/{print \$2}" | head -n 1)
KP_=$(ps -ef | awk "/python3 KP.py KP/{print \$2}" | head -n 1)
GT_=$(ps aux | grep 'GenTargets.sh' | awk '{print $2}' | head -n 1)

kill -9 $Radar1_
kill -9 $Radar2_
kill -9 $Radar3_
kill -9 $ZRDN1_
kill -9 $ZRDN2_
kill -9 $ZRDN3_
kill -9 $SPRO1_
kill -9 $KP_
kill -9 $GT_

python3 KillMessage.py Radar1
python3 KillMessage.py Radar2
python3 KillMessage.py Radar3
python3 KillMessage.py ZRDN1
python3 KillMessage.py ZRDN2
python3 KillMessage.py ZRDN3
python3 KillMessage.py SPRO1
python3 KillMessage.py KP

echo Система остановлена!