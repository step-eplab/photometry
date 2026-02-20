#!/bin/bash

dir_night=$1
dir_data=$2
dir_config=$3
catalog_path=$4
target=$5

echo $dir_night
echo $dir_data
echo $dir_config
echo $catalog_path
echo $target
printf '\n\n\n\n\n\'

############################################################################
START_TIME=$SECONDS

if [ -d "$dir_data" ];
then
echo "$dir_data does exist."
else
mkdir $dir_data
fi

printf '\n\n\n\n\n1.createMasters.py\n'
python master_calibration_frames.py $dir_data $dir_night $target

printf '\n\n\n\n\n2.procImages.py\n'
python reduction.py $dir_night $dir_data $dir_config $target 

printf '\n\n\n\n\n3.createLC.py\n'
python -W"ignore" raw_light_curves_night_part.py $dir_data $target $catalog_path

############################################################################
rm -r $dir_data/Calibrated
#rm -r $dir_data/Cat
#rm -r $dir_data/WCS
rm -r $dir_data/XYMag
#rm $dir_data/MJD.npy

ELAPSED_TIME=$(($SECONDS - $START_TIME))
echo $ELAPSED_TIME
printf '\n\n\n\n\n\'
