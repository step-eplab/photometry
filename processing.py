#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 20:57:52 2024

@author: fedora

"""
import os	
import sys
import glob
import numpy as np

import lzma
from time import time
import multiprocessing
import subprocess

from astropy.io import fits
from astropy.time import Time

from utils import trim_frames, save_frame 
from calibration import calibrate
from astrometry import run_astrometry

#######################################

def process(MJD, file, k, Master, dir_cal, dir_wcs, Params_dict, Params_list,
                            reduc=1, astrometry=1, photometry=1, remove_images=1):
    if file[-2:]=='xz':
        file_open = lzma.open(file)
        file = file[:-3]
    else:
        file_open = file
    name = file[file.find(target):-4]
    with fits.open(file_open) as f:
        hdr = f[0].header
        frame = f[0].data
    frame = trim_frames(frame)
    MJD[name] = Time(hdr['UNIXTIME'], format='unix').mjd + hdr['EXPTIME'] / 2 / 86400

    #######################################
    if reduc:
        image_cb = calibrate(frame, k, Master, dir_cal)
    
    g = [0, 1500, 1000, 3096, 2596, 4096]
    parts = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]]
    Y_grid = [g[:2], g[2:4], g[4:]]
    X_grid = Y_grid
    for part_i in range(9):
        name_i = name + '_' + str(part_i)
        n_y, n_x = parts[part_i]
        X_i, Y_i = X_grid[n_x], Y_grid[n_y]

        image_i = trim_frames(image_cb, Y_i, X_i)
        save_frame(image_i, name=name_i, dir_save=dir_cal, hdr=hdr)
    #######################################
        if astrometry:
            image_astrom = dir_cal + name_i + '.fits'
            run_astrometry(hdr, image_astrom, Params_dict, Params_list, 
                           target, dir_xym)
    #######################################
        if photometry:
            with open(se_config_2, 'r') as f:
              filedata = f.read()      
            filedata = filedata.replace('test.cat', dir_cat + name_i + '.cat')
        
            se_config_tmp = se_config_2 + '_' + name_i
            with open(se_config_tmp, 'w') as f:
              f.write(filedata)
              
            image_photom = dir_wcs + name_i + '.new'
            cmd = 'sex ' + image_photom + ' -c ' + se_config_tmp
            subprocess.run(cmd, shell=True)

            os.remove(se_config_tmp)

        if remove_images:
            os.remove(image_astrom)
            os.remove(image_photom)

    return MJD

if len(sys.argv)>1:
    dir_data0 = sys.argv[1]
    dir_data = sys.argv[2]
    dir_config = sys.argv[3]
    target = sys.argv[4]

se_config_1 = dir_config + 'astro.sex'
se_config_2 =  dir_config + 'photo.sex'    

dir_master = dir_data + 'Master/'

dir_cat = dir_data + 'Cat/'
dir_cal = dir_data + 'Calibrated/'
dir_wcs = dir_data + 'WCS/'
dir_xym = dir_data + 'XYMag/'

image_files = glob.glob(dir_data0 + '**/*' + target + '*.fit*', recursive=True)
image_files = np.sort(image_files)

for d in [dir_data, dir_wcs, dir_xym, dir_cat, dir_cal]:
    if not os.path.isdir(d):
        os.mkdir(d)

#######################################
Params_dict = {
    '-D': dir_wcs,
    '--source-extractor-path': '/usr/bin/sex',
    '--source-extractor-config': se_config_1,
    '-5': '2.0',
    '-L': '1.3',
    '-H': '1.4',
    '-u': 'app',
    '--x-column': 'X_IMAGE',
    '--y-column': 'Y_IMAGE',
    '--sort-column': 'MAG_AUTO',
#    '--config':am_config,

    '--uniformize': '0',
   # '-d': '11-20',
    '-t': '4',
    #'-N': 'none',
    '-R': 'none',
    '-B': 'none',
    '-M': 'none',
    '-S': 'none',
    '-U': 'none',
    }

Params_list = ['--use-source-extractor', '-g', '-O',
               '--temp-axy', '-r', '-p', '--timestamp', '--no-remove-lines',
               '--no-verify-uniformize', '--sort-ascending']

####################################### 
s = ''
k = 0
Master = []
if os.path.isfile(dir_master + 'M_dark.fits'):
    with fits.open(dir_master + 'M_dark.fits') as f:
        M_dark = f[0].data
    Master.append(M_dark)
    s+=' dark '
    k+= 1
    
    
if os.path.isfile(dir_master + 'M_flat.fits'):
    with fits.open(dir_master + 'M_flat.fits') as f:
        M_flat = f[0].data
    Master.append(M_flat)
    s+=' flat '
    k+=2
    
t0 = time()
n = os.cpu_count()
N = len(image_files)//n + 1
print(s + 'subsctract')

#image_files = image_files
print(image_files)

if k > 0:
    manager = multiprocessing.Manager()
    MJD = manager.dict()
    for i in range(N):
        image_files_i = image_files[i * n : (i + 1) * n]
        
        processes = []
        for file in image_files_i:
            name = file[file.find(target):]
            print(name, end=', ')  
        
            p = multiprocessing.Process(target=process, args=(MJD, file, k,
                                    Master, dir_cal, dir_wcs, Params_dict, Params_list))
            processes.append(p)
            p.start()
            
        for p in processes:
            p.join()
        
    K = list(MJD.keys())
    V = list(MJD.values())  
    np.save(dir_data + 'MJD.npy', np.array([K, V]).T)
    print(time() - t0)
