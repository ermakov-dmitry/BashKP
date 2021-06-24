#!/bin/bash

./GenTargets.sh &
python3 KP.py KP &
python3 Radar.py Radar1 &
python3 Radar.py Radar2 &
python3 Radar.py Radar3 &
python3 ShootObject.py SPRO1 &
python3 ShootObject.py ZRDN1 &
python3 ShootObject.py ZRDN2 &
python3 ShootObject.py ZRDN3