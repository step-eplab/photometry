#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 18:10:09 2026

@author: fedora
"""

import os
import sys
import glob
from astropy.io import fits

from _funcs import read_fits, collect_frames, trim_frames, combine_frames

def create_master(files, multiproc, mode, img_size_X, img_size_Y, 
                  substract_frame=0, save_path=False):
    Stack = collect_frames(files, multiproc)
    Stack = trim_frames(Stack, Y=img_size_Y, X=img_size_X)
    Master = combine_frames(Stack, mode, M_dark)
    if save_path:
        fits.writeto(save_path, Master)  
    return Master

###############################################################################
if len(sys.argv)>1:
    target = sys.argv[3]
    dir_raw = sys.argv[2]
    dir_res = sys.argv[1]
else:
    target = 'WD0209+210'
    dir_raw = '/home/fedora/astronomy/STEP/main/copy/F4/raw/24.11.10/'
    dir_res = '/home/fedora/astronomy/STEP/main/copy/F4/results/24.11.10/'

min_targets = 30
img_size_X = [36, 4132]
img_size_Y = [21, 4117]
N_dark = 3
N_flat = 3
multiproc = False
###############################################################################
dir_master = dir_res + 'Master/'
os.makedirs(dir_master, exist_ok=True)
image_files = glob.glob(dir_raw + '**/*' + target + '*.fit*', recursive=True)

if len(image_files) > min_targets:
    print('create M_dark')
    MDark_path = dir_master + 'M_dark.fits'
    MDark_here = os.path.isfile(MDark_path)
    M_dark = 0
    if not MDark_here:
        dark_files = glob.glob(dir_raw + '**/*dark*', recursive=True)[:N_dark]
        if len(dark_files)>0:
            M_dark = create_master(dark_files, multiproc, 'Dark',
                                   img_size_X, img_size_Y, 
                                   save_path=MDark_path)
        else:
            print('There are no dark_frames')

    else:
        print('M_DARK exists')
    print('create M_flat')
    MFlat_path = dir_master + 'M_flat.fits'
    MFlat_here = os.path.isfile(MFlat_path)
    if not MFlat_here:
        flat_files = glob.glob(dir_raw + '**/*flat*', recursive=True)[:N_flat]
        if len(flat_files)>0:
            if MDark_here & (type(M_dark)==int):
                M_dark = read_fits(Stack=[], file=MDark_path)[0]
            M_flat = create_master(flat_files, multiproc, 'Flat', 
                                   img_size_X, img_size_Y, M_dark,
                                   save_path=MFlat_path)
        else:
            print('There are no flat_frames')
    else:
        print('M_FLAT exists')
else:
    print(f'There are no {target} images')
