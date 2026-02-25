#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 20:02:26 2024

@author: fedora
"""

import lzma
import numpy as np
import multiprocessing

from astropy.io import fits
from astropy.stats import SigmaClip

def read_fits(Stack, file):
    if file[-2:]=='xz':
        file_open = lzma.open(file)
        file = file[:-3]
    else:
        file_open = file

    with fits.open(file_open) as f:
        frame = f[0].data
    Stack.append(frame)
    return Stack
    
def collect_frames(files, multiproc):
    if multiproc:
        manager = multiprocessing.Manager()
        Stack = manager.list()
        processes = []
        for file in files:
            p = multiprocessing.Process(target=read_fits, args=(Stack, file))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        Stack = list(Stack)
    else:
        Stack = []
        for file in files:
            if file[-2:]=='xz':
                file_open = lzma.open(file)
                file = file[:-3]
            else:
                file_open = file
    
            with fits.open(file_open) as f:
                frame = f[0].data
            Stack.append(frame)
    return Stack

def trim_frames(frames, X, Y):    
    if type(frames)==list:
        for i in range(len(frames)):
            frames[i] = frames[i][Y[0]:Y[1], X[0]:X[1]]
    else:
        frames = frames[Y[0]:Y[1], X[0]:X[1]]
    return frames

def combine_frames(Stack, mode, substract_frame=0):
    print('combine frames')
    M = []
    if mode=='Dark':
        for i, dark in enumerate(Stack):
            print(i, end=', ')
            med = np.median(dark)
            sigma_mask = SigmaClip()(dark).mask
            dark[sigma_mask] = med
            M.append(dark)
        Master = np.mean(M, 0)
    elif mode=='Flat':
        for i, flat in enumerate(Stack):
            print(i, end=', ')
            M.append(flat) 
        Master = np.median(Stack, 0) - substract_frame
        norm = np.quantile(Master.flatten(), 0.95)
        Master = Master / norm
    Master = np.float32(Master)
    return Master

def save_frame(frame, name, dir_save, hdr=0, overwrite=True):
    #if not os.path.isdir(dir_save):
    #    os.mkdir(dir_save)
    if type(hdr)!=int:
        fits.writeto(dir_save + name + '.fits', frame, hdr, overwrite=overwrite)   
    else:
        fits.writeto(dir_save + name + '.fits', frame, overwrite=overwrite)  

def sigma_clip(img, n=3):
    med = np.nanmedian(img)
    std = np.nanstd(img)
    u = abs(img - med) > n * std
    img[u] = med
    return img

