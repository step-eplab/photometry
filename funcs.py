#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 20:02:26 2024

@author: fedora
"""
import numpy as np
import os
from astropy.io import fits

import lzma

def sigma_clip(img, n=3):
    med = np.nanmedian(img)
    std = np.nanstd(img)
    u = abs(img - med) > n * std
    img[u] = med
    return img

def trimFrames(frames, Y=[], X=[]):
    if len(Y)==0:
        Y = [21, 4117] #[1385, 2750] #[21, 4117] #
    if len(X)==0:
        X = [36, 4132] #[1385, 2750]  #[36, 4132] #
    
    if type(frames)==list:
        for i in range(len(frames)):
            frames[i] = frames[i][Y[0]:Y[1], X[0]:X[1]]
    else:
        frames = frames[Y[0]:Y[1], X[0]:X[1]]
        
    return frames

def collectFrames(files_list):
    Stack = []
    for file in files_list:
        if file[-2:]=='xz':
            file_open = lzma.open(file)
            file = file[:-3]
        else:
            file_open = file

        with fits.open(file_open) as f:
            frame = f[0].data
        Stack.append(frame)
    return Stack



def saveFrame(frame, name, dir_save, hdr=0, overwrite=True):
    #if not os.path.isdir(dir_save):
    #    os.mkdir(dir_save)
    if type(hdr)!=int:
        fits.writeto(dir_save + name + '.fits', frame, hdr, overwrite=overwrite)   
    else:
        fits.writeto(dir_save + name + '.fits', frame, overwrite=overwrite)  









