#!/bin/bash

source ./InitParameters.sh

mkdir -p Files
filename=`pwd`/Files/LastTargets.csv
last_targets_id=$filename
:> $last_targets_id
num_targets=30  # number of latest targets
targets_dir=/tmp/GenTargets/Targets/

# first step (gen initial condition)
OldStepDir=`pwd`/Files/TargetsDataOldStep.csv
CurStepDir=`pwd`/Files/TargetsDataCurStep.csv

ls -t /tmp/GenTargets/Targets/ | sort | tail -n $num_targets > $last_targets_id  # find last n files
cat /dev/null > $OldStepDir
while read line
    do
      echo -n ${line:12}',' >> $OldStepDir
      cat $targets_dir$line >> $OldStepDir
  done < $filename

for ((;;))
do
  sleep 1  # delta_t >= Sleeptime

  ls -t /tmp/GenTargets/Targets/ | sort | tail -n $num_targets > $last_targets_id  # find last n files
  cat /dev/null > $CurStepDir

  while read line
    do
      echo -n ${line:12}',' >> $CurStepDir
      cat $targets_dir$line >> $CurStepDir
  done < $filename

  # calc
  python3 ParseTargets.py

  cat $CurStepDir > $OldStepDir  # rewrite (x_k -> x_{k-1})
  echo iter
done

#python3 ParseTargets.py


