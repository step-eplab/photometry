#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 13:54:41 2024

@author: fedora
"""

import os
import json

import numpy as np
import pandas as pd

import astropy.io.ascii as asc

def run(config_name, date, dir_save):    
    with open(config_name, 'r') as file:
        configs = json.load(file)
    N_col = configs['PHOT_APERTURES'].count(',') + 1
    columns = np.concatenate(([''], '_' + np.arange(1, N_col).astype(str)))
    #############################
    date = date.replace('.','')
    
    dir_cat = dir_save + 'Cat/'
    dir_lc = dir_save + 'LC/'
    
    files = pd.Series(np.sort(os.listdir(dir_cat)))
    
    if not os.path.isdir(dir_lc):
        os.mkdir(dir_lc)
    
    #############################
    time = np.load(dir_save + 'time.npy', allow_pickle=True)
    if time[0, 1].find('.')<7:
        dt = 2400000.5
    else:
        dt = 0
    JD = np.float64(time[:,1]) + dt
    
    names = []
    for name_file in files:
        names.append(name_file[:-4])
    
    files = files[np.isin(names, time[:,0])]
    files = np.sort(files)
    
    Mag = {}
    G_inx = {}
    DFs = []
    for i in range(len(columns)):
        DFs.append(pd.DataFrame(dtype=float))
    
    # images
    for file in files:
        print(file)
        name = file[:-4]
        cat_name = dir_cat + name + '.cat'
        data = asc.read(cat_name).to_pandas(index='NUMBER')
        
        data = data.sort_values(['VECTOR_ASSOC', 'MAG_APER'], ignore_index=True)
        data = data.drop_duplicates(subset='VECTOR_ASSOC')
        G_inx = data['VECTOR_ASSOC'].values
        
        # apertures
        for i, col in enumerate(columns):
            Mag = data[f'MAG_APER{col}'].values

            df = pd.DataFrame(data=Mag, index=G_inx, columns=JD[time[:,0]==name], dtype=float)
            DFs[i] = pd.concat((DFs[i], df), axis=1)

    for i, col in enumerate(columns):
        name_df = f'{dir_lc}LC_{date}{col}.csv'
        print(f'SAVE DataFrame {name_df}')
        DFs[i].to_csv(name_df, index_label='g_inx')








