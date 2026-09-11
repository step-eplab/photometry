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

def read_fits(file, Stack=[]):
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
    print(f'\n    Сollect frames: N={len(files)}, multiproc={multiproc}')
    if multiproc:
        manager = multiprocessing.Manager()
        Stack = manager.list()
        processes = []
        for file in files:
            p = multiprocessing.Process(target=read_fits, args=(file, Stack))
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
    print(f'\n    Trim frames: {X, Y}')
    if type(frames)==list:
        for i in range(len(frames)):
            frames[i] = frames[i][Y[0]:Y[1], X[0]:X[1]]
    else:
        frames = frames[Y[0]:Y[1], X[0]:X[1]]
    return frames



def combine_frames(Stack, mode, substract_frame=0):
    print('\n    Сombine frames')
    Stack = np.asarray(Stack, dtype=np.float32)
    if mode == 'Dark':
        Median = np.median(Stack, axis=0)
        dif = np.abs(Stack - Median).mean(axis=(1, 2))
        good = (dif/np.median(dif)) < 2
        Stack = Stack[good]
        print(f'    {sum(good)}/{len(good)} are used')
    if mode == 'Flat':
        Stack -= substract_frame
        lvl_norm = np.quantile(Stack, 0.95, axis=(1, 2), keepdims=True)
        Stack /= lvl_norm
    Master = np.median(Stack, axis=0)
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


