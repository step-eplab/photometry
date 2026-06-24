#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 14:07:59 2026

@author: fedora
"""

import os
import json
from createCF import run as run_createCF
from procRI import run as run_procRI
from createRLC import run as run_createRLC

config_name_paths = '../paths_F3.json'
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

config_name_RI = dir_configs + 'procRI.json'  
config_name_RLC = dir_configs + 'createRLC.json'
config_name_CF = dir_configs + 'createCF.json'

dates = os.listdir(dir_raw)


for date in dates[1:2]:    
    #config_name_CF = f'configs/createCF_{date}.json'
    
    dir_data = dir_raw + date + '/'
    dir_save = dir_res + date + '/'

    run_createCF(config_name_CF, target, dir_data, dir_save, 
                 img_size_X, img_size_Y)

    run_procRI(config_name_RI, target, catalog_path, 
               dir_data, dir_save, dir_configs, 
               img_size_X, img_size_Y, N_images=10)
    run_createRLC(config_name_RLC, date, dir_save)


#F = read_fits('/home/fedora/astronomy/STEP/main/data/F4/result/24.11.10/Master/M_flat.fits', [])[0]
#D = read_fits('/home/fedora/astronomy/STEP/main/data/F4/result/24.11.10/Master/M_dark.fits', [])[0]









