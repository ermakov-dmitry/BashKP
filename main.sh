#!/bin/bash

source ./InitParameters.sh

mkdir -p Files
last_targets=`pwd`/Files/LastTargets.csv
targets_dir=/tmp/GenTargets/Targets/
OldStepDir=`pwd`/Files/TargetsDataOldStep.csv
CurStepDir=`pwd`/Files/TargetsDataCurStep.csv
:> $last_targets
num_targets=5  # number of last targets

# first step (gen initial condition)
ls -t $targets_dir | sort | tail -n $num_targets > $last_targets  # find last n files
cat /dev/null > $OldStepDir
while read line
    do
      echo -n ${line:12}',' >> $OldStepDir
      cat $targets_dir$line >> $OldStepDir
  done < $last_targets

delta_t=10
for ((;;))
do

  sleep $delta_t  # delta_t >= Sleeptime
  ls -t $targets_dir | sort | tail -n $num_targets > $last_targets  # find last n files
  cat /dev/null > $CurStepDir

  while read line
    do
      echo -n ${line:12}',' >> $CurStepDir
      cat $targets_dir$line >> $CurStepDir
  done < $last_targets

  # calc
  python3 ParseTargets.py
  cat $CurStepDir > $OldStepDir  # rewrite (x_k -> x_{k-1})
  # echo iter
done

#python3 ParseTargets.py


