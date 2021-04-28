#!/bin/bash

source ./InitParameters.sh

filename=LastTargets.csv
last_targets_id=$filename
:> $last_targets_id
num_targets=10  # number of latest targets
targets_dir=/tmp/GenTargets/Targets/
for ((;;))
do
  ls -t /tmp/GenTargets/Targets/ | tail -n $num_targets >> $last_targets_id
  sleep 5
  # тут будет что-то происходить
  while read line
    do
      echo ${line:12}; cat $targets_dir$line
  done < $filename
  # до сюда
  cat /dev/null > $filename
  echo iter
done

#python3 ParseTargets.py


