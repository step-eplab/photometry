#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 14:44:37 2026

@author: fedora
"""

import numpy as np

from astropy.stats import SigmaClip
from photutils.background import Background2D, MedianBackground

def calibrate(frame, k, Master, dir_cal):
    if k==1:
        M_dark = Master[0]
        image_c = frame - M_dark
    if k==3:
        M_dark, M_flat = Master
        image_c = (frame - M_dark) / M_flat
    image_c = np.float32(image_c)
#    return image_c

    bkg_estimator = MedianBackground()
    bkg = Background2D(image_c, (28, 28), filter_size=(7, 7),
                           sigma_clip=SigmaClip(sigma=5), bkg_estimator=bkg_estimator)

    image_cb = image_c - bkg.background
    '''
    sat_lvl = 50e3
    sat = image_cb>sat_lvl
    image_cb[sat] = np.nan
    '''
    image_cb = np.float32(image_cb)
    return image_cb
