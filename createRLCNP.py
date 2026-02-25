#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 13:54:41 2024

@author: fedora
"""

import os
import sys

import numpy as np
import pandas as pd

import astropy.io.ascii as asc

if len(sys.argv)>1:
    dir_data = sys.argv[1]
    target = sys.argv[2]
    catalog_path = sys.argv[3]

else:
    dir_data ='/Data/oleg/F1_EGGR-381/2020/20.09.20/' # '/home/fedora/astronomy/STEP/main/data/F1/images/20.09.20/'
    target = 'EGGR381'
    catalog_path = '/home/oleg/oleg/STEP/catalogs/F1_2405.list'   #'/home/fedora/astronomy/STEP/F1_24.list'

#############################
date = dir_data.replace('.','')[-7:-1]      

dir_cat = dir_data + 'Cat/'
dir_lc = dir_data + 'LC/'

files = pd.Series(np.sort(os.listdir(dir_cat)))
n_part = files.str[-5:-4]

for pi in range(9):
    part_i = str(pi)
    u_i = n_part==part_i
    print(dir_lc + 'LC_' + date + '_' + part_i + '.csv') 


    if not os.path.isdir(dir_lc):
        os.mkdir(dir_lc)

    namew_files = files[u_i].values
    print(namew_files)    
     

#############################
    MJD = np.load(dir_data + 'MJD.npy', allow_pickle=True)
    JD = np.float64(MJD[:,1]) + 2400000.5

    names = []
    for name_file in namew_files:
        names.append(name_file[:-6])
    print(names, MJD)
    namew_files = namew_files[np.isin(names, MJD[:,0])]
    namew_files = np.sort(namew_files)

    Mag = {}
    G_inx = {}
    DF = pd.DataFrame(dtype=float)

    for namew in namew_files:
        print(namew)
        name = namew[:-4]
        name_i = name[:-2]
        cat_name = dir_cat + name + '.cat'
        data = asc.read(cat_name).to_pandas(index='NUMBER')

        data = data.sort_values(['VECTOR_ASSOC', 'MAG_APER'], ignore_index=True)
        data = data.drop_duplicates(subset='VECTOR_ASSOC')

        Mag = data['MAG_APER_1'].values
        G_inx = data['VECTOR_ASSOC'].values

        df = pd.DataFrame(data=Mag, index=G_inx, columns=JD[MJD[:,0]==name_i], dtype=float)
        DF = pd.concat((DF, df), axis=1)

        #os.remove(cat_name)

    name_df = dir_lc + 'LC_' + date + '_' + part_i + '.csv'
    print('SAVE DataFrame ' +  name_df)
    DF.to_csv(name_df, index_label='g_inx')









