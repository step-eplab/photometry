#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 14:57:05 2026

@author: fedora
"""

import subprocess

def runAstrometry(hdr, file, Params_dict, Params_list,
                  target, dir_xym):
    name = file[file.find(target):-5]
    ra0 = hdr['TAGRA']
    dec0 = hdr['TAGDEC']
    Params_dict['-k'] = dir_xym + name + '.axy'
    Params_dict['-3'] =  str(ra0) # '3.05730540959', # 
    Params_dict['-4'] =  str(dec0) # '50.4192709867', #
    
    SF_params = ''
    for k in Params_dict.keys():
        SF_params += k + ' ' + Params_dict[k] + ' '
        
    SF_params += ' '.join(Params_list) + ' '
    SF_comand = 'solve-field ' + SF_params + file 
    
    subprocess.run(SF_comand, shell=True) 
