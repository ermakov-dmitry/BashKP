#!/bin/bash

source ./InitParameters.sh

rm -rf Files/
mkdir -p Files
last_targets=`pwd`/Files/LastTargets
targets_dir=/tmp/GenTargets/Targets/
StepDir=`pwd`/Files/TargetsDataStep.csv
:> $last_targets
num_targets=50  # number of last targets

delta_t=1
start=`date +%s`
for ((;;))
do

  sleep $delta_t  # delta_t >= Sleeptime
  ls -t $targets_dir | tail -n $num_targets > $last_targets  # find last n files  sort |
  cat /dev/null > $StepDir
  end=`date +%s`
  runtime=$((end-start))

  # echo $runtime
  while read line
    do
      echo -n ${line:12}',' >> $StepDir
      cat $targets_dir$line >> $StepDir
  done < $last_targets

  python3 ParseTargets.py
done


