#!/usr/bin/env python

import os
import pandas as pd
import re
import numpy as np
import sys

'''
Run this script as EKKO_general.py {summaryfile}
Ex. EKKO_general.py 2_145_summary.cdxs
'''

def find_scanfile():
    '''
    Returns
    -------
    str
        scan summary file
    '''
    for file in os.listdir('.'):
        if file[-5:] == ".cdxs" or file[-5:] == ".CDXS":
            scan_file = str(file)
    if scan_file == '':
        print("No scans were found.")
        return 1
    return(scan_file)

def get_block_size(scan_file):
    '''
    Parameters
    ----------
    scan_file : str
        scan file name i.e. 2_145_summary.cdxs

    Returns
    -------
    TYPE : int
        size of block for the scans i.e. 4 for a scan of 3 wavelengths (additional header for well name included)

    '''
    raw = pd.read_csv(scan_file, skiprows=3,)
    raw = raw["Process Name:"][0]
    digits = re.findall(r'\b\d+\b', raw)
    block_size = (int(digits[1]) - int(digits[0])) / int(digits[2]) +2
    return int(block_size)

def get_scandata(scan_file):
    '''
    Parameters
    ----------
    scan_file : str
        Name of scan file

    Returns
    -------
    df : Pandas dataframe
        Raw output of EKKO plate reader summary file (columns = WL, CD-mDeg, and ABS)
    '''
    
    df = pd.read_csv(scan_file, skiprows=11, delimiter="\t", error_bad_lines=False, usecols=["WL","CD-mDeg","ABS"])
    df.drop(df.tail(17).index, inplace=True)
    return df

def get_wavelengths(scan_data, block_size):
    wavelengths = scan_data["WL"][1:block_size] #Extracts wavelengths from first well plate reading. Assumes all wells measured same WL
    return wavelengths

def get_combined_output(scan_data, wavelengths, block_size):
    scan_list = np.array_split(scan_data, len(scan_data["WL"])/block_size)
    for i in range(len(scan_list)):
        well = scan_list[i]
        well = well.reset_index(drop=True)
        well["ABS"][0] = well["WL"][0]
        well["CD-mDeg"][0] = well["WL"][0]
        well = well.columns.to_frame().T.append(well, ignore_index=True)
        scan_list[i] = well
    df = scan_list[0]
    for item in range(len(scan_list) - 1):
        df = pd.concat([df, scan_list[item + 1]], ignore_index=False, axis=1)
    return df

def get_cd(data, wavelengths):
    cd_only = pd.DataFrame(wavelengths)
    
    cd_only.loc[-1] = ""
    cd_only.loc[-2] = ""
    cd_only.index = cd_only.index + 2
    cd_only = cd_only.sort_index().reset_index(drop=True)

    cd_only = cd_only.join(data["CD-mDeg"])
    return cd_only

def get_abs(data, wavelengths):
    abs_only = pd.DataFrame(wavelengths)
    
    abs_only.loc[-1] = ""
    abs_only.loc[-2] = ""
    abs_only.index = abs_only.index + 2
    abs_only = abs_only.sort_index().reset_index(drop=True)
    
    abs_only = abs_only.join(data["ABS"])
    return abs_only

def main():
    scan_file = find_scanfile()    #Uncomment this line to make script find scan file
    #scan_file = sys.argv[1]
    block_size = get_block_size(scan_file)
    
    scan_data = get_scandata(scan_file)

    wavelengths = get_wavelengths(scan_data, block_size)
    
    data = get_combined_output(scan_data, wavelengths, block_size)
    
    cd_only = get_cd(data, wavelengths)
    abs_only = get_abs(data, wavelengths)
    
    data = cd_only.merge(abs_only, left_index=True, right_index=True, how='inner')
    
    data.to_csv('{}_rearranged.csv'.format(scan_file[:-5]), index=False, header=False)
    
if __name__ == '__main__': 
    #main()
    pass