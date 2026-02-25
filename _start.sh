#!/bin/bash

field=3

dir_raw='/home/obs/robotel1_2024/' # #/Data/robotel1_data/
dir_config='/home/oleg/oleg/STEP/configs/'

if [[ "$field" == "1" ]]; then
    dir_res=#'/Data/oleg/F1_EGGR-381/2020/'
    catalog_path='/home/oleg/oleg/STEP/catalogs/F1_2405.list'
    target='EGGR381'
elif [[ "$field" == "2" ]]; then
    dir_res='/Data/oleg/F2/2022/'
    catalog_path='/home/oleg/oleg/STEP/catalogs/F2_2405.list'
    target='GRW+708247'
else
    dir_res='/Data/oleg/F3_GD_356/'
    catalog_path='/home/oleg/oleg/STEP/catalogs/GD_356.list'
    target='GD356'
fi

###!!!  CHECK ASSOC_NAME in dir_config photo.sex

for night in 24.02* 24.03* 24.04* 24.05* 24.06* 24.07* 24.08*
do
    echo $night
    for dir_night in $dir_raw$night
    do
        dir_data=${dir_night/$dir_raw/"$dir_res"}
        echo $dir_night
        echo $dir_data
        sh startProc.sh $dir_night/ $dir_data/ $dir_config $catalog_path $target
        #sleep 3
    done
done

