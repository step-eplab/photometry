#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 14:07:59 2026

@author: fedora
"""

import os
import sys
import json
import glob
import numpy as np
import subprocess

from createCF import run as run_createCF
from procRI import run as run_procRI
from createRLC import run as run_createRLC

def get_dates(dir_raw, configs_main):
    year = configs_main['year']
    months = configs_main['month']
    days = configs_main['days']
    
    dates_here = np.array(os.listdir(dir_raw))
    dates = []
    for month, days_m in zip(months, days):
        days_grid = np.arange(days_m[0], days_m[1])
        for day in days_grid:
            if day<10:
                day = '0' + str(day)
            dates.append(f'{year}.{month}.{day}')
    dates = dates_here[np.isin(dates_here, dates)]
    return dates


def main():
    if len(sys.argv)>1:
        config_name_paths = sys.argv[1]
    else:
        config_name_paths = '../paths_F4.json'
    
    with open(config_name_paths, 'r') as file:
        configs_paths = json.load(file)
    dir_raw = configs_paths['dir_raw_images']
    dir_res = configs_paths['dir_res']
    dir_configs = configs_paths['dir_configs']
    catalog_path = configs_paths['dir_cat'] + configs_paths['cat_name']
    
    config_name_main = dir_configs + 'photometry.json'   
    with open(config_name_main, 'r') as file:
        configs_main = json.load(file)
    target = configs_main['target']
    img_size_X = configs_main['img_size_X']
    img_size_Y = configs_main['img_size_Y']
    min_targets = configs_main['min_targets']
    N_images = configs_main['N_images']
    config_name_RI = dir_configs + 'procRI.json'  
    config_name_CF = dir_configs + 'createCF.json'
    #config_name_RLC = dir_configs + 'createRLC.json'
    
    dates = get_dates(dir_raw, configs_main)

    for date in dates:
        dir_data = dir_raw + date + '/'
        image_files = glob.glob(dir_data + '**/*' + target + '*.fit*', recursive=True)
   
        if len(image_files) > min_targets:
            dir_save = dir_res + date + '/'
        
            run_createCF(config_name_CF, dir_data, dir_save, 
                         img_size_X, img_size_Y)
    
            run_procRI(config_name_RI, target, catalog_path, 
                       dir_data, dir_save, dir_configs,
                       img_size_X, img_size_Y, N_images=N_images)
            run_createRLC(config_name_RI, date, dir_save)
            
            for name in ['Calibrated', 'Cat', 'WCS', 'XYMag', 'time.npy']:
                subprocess.run(f'rm -r {dir_res}{date}/{name}', shell=True)
            
        else:
            print(f'There are no {target} images')
            print(f'path: {dir_data}')


if __name__ == "__main__":
    main()

