#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 14:07:59 2026

@author: fedora
"""

import json
from createCF import run as run_createCF
from procRI import run as run_procRI
from createRLC import run as run_createRLC

config_name_main = 'configs/main.json'   
config_name_pathes = '../pathes.json'   

with open(config_name_main, 'r') as file:
    configs_main = json.load(file)
target = configs_main['target']
img_size_X = configs_main['img_size_X']
img_size_Y = configs_main['img_size_Y']

with open(config_name_pathes, 'r') as file:
    configs_main = json.load(file)

dir_raw = configs_main['dir_raw']
dir_res = configs_main['dir_res']
catalog_path = configs_main['catalog_path']

config_name_RI = 'configs/procRI.json'  
config_name_RLC = 'configs/createRLC.json'


dates = ['28.05.26'] # '26.04.26', 

for date in dates:    
    config_name_CF = f'configs/createCF_{date}.json'
    
    dir_data = dir_raw + date + '/'
    dir_save = dir_res + date + '/'

    run_createCF(config_name_CF, target, dir_data, dir_save, img_size_X, img_size_Y)
    run_procRI(config_name_RI, target, catalog_path, dir_data, dir_save,
               img_size_X, img_size_Y) #, N_images=5)
    run_createRLC(config_name_RLC, date, dir_save)















