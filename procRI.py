#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 20:57:52 2024

@author: fedora

"""

import os

import json

import glob
import numpy as np

import lzma
from time import time
import multiprocessing
import subprocess

from astropy.io import fits

from funcs import trim_frames, save_frame

from astropy.time import Time
from astropy.stats import SigmaClip
from photutils.background import Background2D, MedianBackground

###############################################################################
def runReduce(frame, k, Master, dir_cal, back=True):
    if k==1:
        M_dark = Master[0]
        image_c = frame - M_dark
    if k==3:
        M_dark, M_flat = Master
        image_c = (frame - M_dark) / M_flat
    image_c = np.float32(image_c)
    if back:
        bkg_estimator = MedianBackground()
        bkg = Background2D(image_c, 50, sigma_clip=SigmaClip(sigma=5),
                           bkg_estimator=bkg_estimator)

        image_cb = image_c - bkg.background
        image_cb = np.float32(image_cb)
        return image_cb
    else:
        return image_c


def runAstrometry(hdr, file, Params_dict, Params_list, target, se_config_1, 
                  name, dir_xym, dir_config, ra=0, dec=0, rad=1):
    # read
    with open(se_config_1, 'r') as f:
      filedata = f.read()      
    filedata = filedata.replace('astrometry.out', dir_config + 'params/astrometry.out')
    # save
    se_config_tmp = se_config_1 + '_' + name
    with open(se_config_tmp, 'w') as f:
      f.write(filedata)
    
    name = file[file.find(target):-5]
    if (ra * dec) != 0:
        Params_dict['-3'] = str(ra)
        Params_dict['-4'] = str(dec)        
    elif np.isin('TAGRA', list(hdr.keys())):
        Params_dict['-3'] = hdr['TAGRA']
        Params_dict['-4'] = hdr['TAGDEC']
    
    Params_dict['-5'] =  str(rad)
    Params_dict['-k'] = dir_xym + name + '.axy'
    Params_dict['--source-extractor-config'] = se_config_tmp
    
    SF_params = ''
    for k in Params_dict.keys():
        SF_params += k + ' ' + Params_dict[k] + ' '
        
    SF_params += ' '.join(Params_list) + ' '
    SF_comand = 'solve-field ' + SF_params + file
    
    subprocess.run(SF_comand, shell=True)
    os.remove(se_config_tmp)
    
    
    
def runPhotometry(image_photom, se_config_2, name, catalog_path, 
                  dir_config, dir_cat, aps):
    # read
    with open(se_config_2, 'r') as f:
      filedata = f.read()      
    filedata = filedata.replace('test.cat', dir_cat + name + '.cat')
    filedata = filedata.replace('photometry.out', dir_config + 'params/photometry.out')
    filedata = filedata.replace('catalog.list', catalog_path)
    filedata = filedata.replace('4,6,8,10', aps)
    # save
    se_config_tmp = se_config_2 + '_' + name
    with open(se_config_tmp, 'w') as f:
      f.write(filedata)

    cmd = 'sex ' + image_photom + ' -c ' + se_config_tmp
    print(cmd)
    subprocess.run(cmd, shell=True)
    
    os.remove(se_config_tmp)



def process(T, file, img_size_X, img_size_Y, k, Master, dir_cal, dir_wcs, 
                            Params_dict, Params_list,
                            target, se_config_1, se_config_2, catalog_path,  
                            dir_config, dir_cat, dir_xym, aps,
                            ra=0, dec=0, rad=0,
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
    frame = trim_frames(frame, Y=img_size_Y, X=img_size_X)
    if np.isin('UNIXTIME', list(hdr.keys())):
        T[name] = Time(hdr['UNIXTIME'], format='unix').mjd + hdr['EXPTIME'] / 2 / 86400
    else:
        T[name] = hdr['JD-HELIO'] #
    #######################################
    if reduc:
        image_cb = runReduce(frame, k, Master, dir_cal)
        save_frame(image_cb, name=name, dir_save=dir_cal, hdr=hdr)
    '''
    g = [0, 1500, 1000, 3096, 2596, 4096]
    parts = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]]
    Y_grid = [g[:2], g[2:4], g[4:]]
    X_grid = Y_grid
    for part_i in range(9):
        name_i = name + '_' + str(part_i)
        n_y, n_x = parts[part_i]
        X_i, Y_i = X_grid[n_x], Y_grid[n_y]
    
        image_i =  trim_frames(image_cb, Y=Y_i, X=X_i)
        save_frame(image_i, name=name_i, dir_save=dir_cal, hdr=hdr)
    #######################################
        if astrometry:
            image_astrom = dir_cal + name_i + '.fits'        
            runAstrometry(hdr, image_astrom, Params_dict, Params_list, target, 
                          se_config_1, name, dir_xym, dir_config,
                          ra, dec, rad)
    #######################################
        if photometry:
            image_photom = dir_wcs + name_i + '.new'
            runPhotometry(image_photom, se_config_2, name, catalog_path, 
                          dir_config, dir_cat, aps)
        if remove_images:
            os.remove(image_astrom)
            os.remove(image_photom)

    return T

    '''
    #######################################
    if astrometry:
        image_astrom = dir_cal + name + '.fits'        
        runAstrometry(hdr, image_astrom, Params_dict, Params_list, target, 
                      se_config_1, name, dir_xym, dir_config,
                      ra, dec, rad)
    #######################################
    if photometry:
        image_photom = dir_wcs + name + '.new'
        runPhotometry(image_photom, se_config_2, name, catalog_path, 
                      dir_config, dir_cat, aps)
    if remove_images:
        os.remove(image_astrom)
        os.remove(image_photom)
    return T






###############################################################################
def run(config_name, target, catalog_path, dir_data, dir_save, dir_configs,
        img_size_X, img_size_Y, N_images=0):    
    
    with open(config_name, 'r') as file:
        configs = json.load(file)
    multiproc_mode = configs['multiproc_mode']
    rad = configs['rad']  
    aps = configs['PHOT_APERTURES']

    ra = configs['ra']
    dec = configs['dec']
    ###############################################################################
    se_config_1 = dir_configs + 'params/astrometry.in'
    se_config_2 =  dir_configs + 'params/photometry.in'
 
    dir_master = dir_save + 'Master/'
    dir_cat = dir_save + 'Cat/'
    dir_cal = dir_save + 'Calibrated/'
    dir_wcs = dir_save + 'WCS/'
    dir_xym = dir_save + 'XYMag/'
    
    image_files = glob.glob(dir_data + '**/*' + target + '*.fit*', recursive=True)
    image_files = np.sort(image_files)
    
    for d in [dir_save, dir_wcs, dir_xym, dir_cat, dir_cal]:
        if not os.path.isdir(d):
            os.mkdir(d)
    
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
    
    Params_dict = {
        '-D': dir_wcs,
        '--source-extractor-path': '/usr/bin/sex',
        #'--config': dir_configs + 'astrometry.cfg',
        '-u': 'app',
        '--x-column': 'X_IMAGE',
        '--y-column': 'Y_IMAGE',
        '--sort-column': 'MAG_AUTO',
        '--uniformize': '0',
        '-R': 'none',
        '-B': 'none',
        '-M': 'none',
        '-S': 'none',
        '-U': 'none',
        '-t': '4'
        }
    Params_list = ['--use-source-extractor', '-g', '-O',
                   '--temp-axy', '-r', '-p', '--timestamp', '--no-remove-lines',
                   '--no-verify-uniformize', '--sort-ascending']
    
    if N_images!=0:
        image_files = image_files[:N_images]

    if k > 0:
        if multiproc_mode:
            manager = multiprocessing.Manager()
            T = manager.dict()
            for i in range(N):
                image_files_i = image_files[i * n : (i + 1) * n]
                
                processes = []
                for file in image_files_i:
                    #name = file[file.find(target):]
                    #print(name, end=', ')  
                
                    p = multiprocessing.Process(target=process, args=(T, file, img_size_X, img_size_Y, k,
                                            Master, dir_cal, dir_wcs, Params_dict, Params_list,
                                            target, se_config_1, se_config_2, catalog_path,
                                            dir_configs, dir_cat, dir_xym, aps,
                                            ra, dec, rad))
                    processes.append(p)
                    p.start()
                for p in processes:
                    p.join()
                
            K = list(T.keys())
            V = list(T.values())  
            np.save(dir_save + 'time.npy', np.array([K, V]).T)
            print(time() - t0)
        else:
            T = {}
            for i, file in enumerate(image_files):
                print(i, end=', ')
                process(T, file, img_size_X, img_size_Y, k, Master, dir_cal, dir_wcs, 
                                Params_dict, Params_list,
                                target, se_config_1, se_config_2, catalog_path,
                                dir_configs, dir_cat, dir_xym, aps,
                                ra, dec, rad,
                                reduc=1, astrometry=1, photometry=1, remove_images=1)
                
                K = list(T.keys())
                V = list(T.values())  
                np.save(dir_save + 'time.npy', np.array([K, V]).T)
