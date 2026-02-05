#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:37:05 2024

@author: fedora

"""

import os
import sys
import glob
import numpy as np

from astropy.io import fits
from astropy.stats import SigmaClip

from funcs import trimFrames, collectFrames, saveFrame

import multiprocessing
import subprocess
import lzma

def CreateMDark(Dark):
    D = []
    i=0
    for dark in Dark:
        print(i, end=', ')
        med = np.median(dark)
        sigma_mask = SigmaClip()(dark).mask
        dark[sigma_mask] = med

        D.append(dark)
        i+=1
    Master = np.mean(D, 0)
    Master = np.float32(Master)
    return Master

def CreateMFlat(Flat, substract_frame=0):
    F = []
    i = 0
    for flat in Flat:
        print(i, end=', ')
        F.append(flat) 
        i+=1
    Master = np.median(Flat, 0) - M_dark
    norm = np.quantile(Master.flatten(), 0.95)
    Master = Master / norm
    Master = np.float32(Master)
    return Master


def MDark(dark_files, multi=0):
    print('Prepare Dark')
    if multi:
        Dark = collectFrames_multi(dark_files)
    else:
        Dark = collectFrames(dark_files)
    Dark = trimFrames(Dark)
    print('Create M_dark')
    Master = CreateMDark(Dark)
    return Master

def MFlat(flat_files, substract_frame=0, multi=0):
    print('Prepare Flat')
    if multi:
        Flat = collectFrames_multi(flat_files)
    else:
        Flat = collectFrames(flat_files)
    Flat = trimFrames(Flat)
    print('Create M_flat')
    Master = CreateMFlat(Flat, M_dark)
    return Master

def readFits(Stack, file):
    if file[-2:]=='xz':
        file_open = lzma.open(file)
        file = file[:-3]
    else:
        file_open = file

    with fits.open(file_open) as f:
        frame = f[0].data
    Stack.append(frame)

def collectFrames_multi(files):
    manager = multiprocessing.Manager()
    Stack = manager.list()
    processes = []
    for file in files:
        p = multiprocessing.Process(target=readFits, args=(Stack, file))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    return list(Stack)


if len(sys.argv)>1:
    dir_data = sys.argv[1]
    dir_data0 = sys.argv[2]
    target = sys.argv[3]


image_files = glob.glob(dir_data0 + '**/*' + target + '*.fit*', recursive=True)

k_t = 0
k_m = 0

if len(image_files) > 30:
    k_t = 1
else:
    print('There are no target images')

dir_master = dir_data + 'Master/'
if not os.path.isdir(dir_master):
    os.mkdir(dir_master)
#k_t=1
if k_t & (not os.path.isfile(dir_master + 'M_dark.fits')):
    dark_files = glob.glob(dir_data0 + '**/*dark*', recursive=True)
    k_m+=1
    print(dark_files)
    if len(dark_files)>0:
        k_m+=1
        M_dark = MDark(dark_files, multi=1)
        saveFrame(M_dark, 'M_dark', dir_master)
else:
    print('M_dark exists or There are no target images')


if k_t & (not os.path.isfile(dir_master + 'M_flat.fits')):
    flat_files = glob.glob(dir_data0 + '**/*flat*', recursive=True)
    if len(flat_files)>0:
        if k_m==0:
            M_dark = collectFrames_multi([dir_master + 'M_dark.fits'])[0]
        elif k_m==1:
            M_dark = 0
        print(flat_files)
        M_flat = MFlat(flat_files, M_dark, multi=1)
        saveFrame(M_flat, 'M_flat', dir_master)
    else:
        pass
else:
    print('M_flat exists or There are no target images')

































