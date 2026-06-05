#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 18:10:09 2026

@author: fedora
"""

import os
import sys
import glob

import json

from astropy.io import fits

from funcs import read_fits, collect_frames, trim_frames, combine_frames

def create_master(files, multiproc, mode, img_size_X, img_size_Y, 
                  substract_frame=0, save_path=False):
    Stack = collect_frames(files, multiproc)
    Stack = trim_frames(Stack, Y=img_size_Y, X=img_size_X)
    Master = combine_frames(Stack, mode, substract_frame)
    if save_path:
        fits.writeto(save_path, Master)  
    return Master

###############################################################################
if len(sys.argv)>1:
    config_name = sys.argv[1]
else:
    config_name = 'configs/conf_createCF.json'
    

with open(config_name, 'r') as file:
    configs = json.load(file)

target = configs['target']
dir_raw = configs['dir_raw']
dir_res = configs['dir_res']

min_targets = configs['min_targets']
img_size_X = configs['img_size_X']
img_size_Y = configs['img_size_Y']
N_dark = configs['N_dark']
N_flat = configs['N_flat']
multiproc = configs['multiproc']

bias_template = configs['bias_template']
dark_template = configs['dark_template']
flat_template = configs['flat_template']

scale_mode = configs['scale_mode']
dark_template_sub = configs['dark_template_sub']
dark_template_scl = configs['dark_template_scl']
dark_exp = configs['dark_exp']
dark_exp_scl = configs['dark_exp_scl']

if scale_mode:
    dark_tmpls = [dark_template_scl, dark_template_sub]
    scale = dark_exp / dark_exp_scl
else:
    dark_tmpls = [dark_template]

###############################################################################
dir_master = dir_res + 'Master/'
os.makedirs(dir_master, exist_ok=True)
image_files = glob.glob(dir_raw + '**/*' + target + '*.fit*', recursive=True)

if len(image_files) > min_targets:
    print('\ncreate M_dark')
    for dark_tmpl in dark_tmpls:
        print('\n', dark_tmpl)
        MDark_path = dir_master + f'M_{dark_tmpl}.fits'
        MDark_here = os.path.isfile(MDark_path)
        M_dark = 0
        if not MDark_here:
            dark_files = glob.glob(dir_raw + f'**/*{dark_tmpl}*.fit', recursive=True)[:N_dark]
            if len(dark_files)>0:
                M_dark = create_master(dark_files, multiproc, 'Dark',
                                       img_size_X, img_size_Y, 
                                       save_path=MDark_path)
            else:
                print('There are no dark_frames')
    
        else:
            print('M_DARK exists')
    print('\ncreate M_flat')
    MFlat_path = dir_master + 'M_flat.fits'
    MFlat_here = os.path.isfile(MFlat_path)
    if not MFlat_here:
        flat_files = glob.glob(dir_raw + f'**/*{flat_template}*.fit', recursive=True)[:N_flat]
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
    print(f'path: {dir_raw}')

### scaling
if scale_mode:
    MBias_path = dir_master + 'M_bias.fits'
    bias_files = glob.glob(dir_raw + f'**/*{bias_template}*.fit', recursive=True)
    if len(bias_files)>0:
        M_bias = create_master(bias_files, multiproc, 'Dark',
                               img_size_X, img_size_Y, 
                               save_path=MBias_path)
    else:
        print('There are no bias_frames')
    
    MDark_path_scl = dir_master + f'M_{dark_template_scl}.fits'
    MDark_path = dir_master + 'M_dark.fits'
    M_dark_scl = read_fits(Stack=[], file=MDark_path_scl)[0]
    
    M_dark = (M_dark_scl - M_bias) * scale + M_bias
    fits.writeto(MDark_path, M_dark)
