
from EKKOTools.EKKOScanFormats import EKKOScanSummary, Well
from EKKOTools.plotting import PlotMultipleSpectra

from itertools import combinations

import pandas as pd
import numpy as np

from EKKOTools.utilities import GetAllSpectraFromWells

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NONE = ''

def CalculateStdSpectra(spectra: list[dict], wl: int = 520, spectra_type = None) -> float:
    '''For a list of spectra, calculate the average std deviation for a given wavelength
    
        Can be used on spectra (dictionaries with wavelengths as keys and intensities as values) directly
        or on Well objects from EKKO tools. If using well objects, the requested spectra_type (cd, abs, or cd_per_abs
        must be requested'''

    if spectra_type == None:
        for s in spectra:
            assert(isinstance(s, dict))
    else:
        for s in spectra:
            assert(isinstance(s, Well))
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['std'].to_dict()[str(wl)]

def CalculateAvgSpectra(spectra: list[dict], wl: int = 520, spectra_type = None) -> float:
    '''For a list of spectra or wells, calculate the average value for a given wavelength
        if wells are supplied, a spectral type must be indicated (cd, abs, or cd_per_abs)
        after which the requested spectra type is obtained from the Well objects'''
    if spectra_type == None:
        for s in spectra:
            assert(isinstance(s, dict))
    else:
        for s in spectra:
            assert(isinstance(s, Well))
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['mean'].to_dict()[str(wl)]

def PickN(l: list[Well], n = 2, wl = 520, spectra_type = None, verbose = False) -> tuple:
    '''Picks the n-closest spectra in a list at some wavelength by calculating the lowest
        standard deviation at of the spectra at the wavellength'''
    combos = list(combinations(l, n))

    if len(l) < n:
        raise Exception('Number of spectra requested exceeds number of spectra provided')

    # Initialize comparison variables with the first combination
    best = combos[0]
    best_std = CalculateStdSpectra(best, wl=wl, spectra_type=spectra_type)
    best_avg = CalculateAvgSpectra(best, wl=wl, spectra_type=spectra_type)

    for combo in combos:
        avg = CalculateAvgSpectra(combo, wl=wl, spectra_type=spectra_type)
        std = CalculateStdSpectra(combo, wl=wl, spectra_type=spectra_type)
        if std < best_std:
            best = combo
            best_std = std
            best_avg = avg

    if verbose:
        _verbose_statistics_printer(analyte=l[0].analyte, best_stddev=best_std, best_avg=best_avg, best_wells=list(best))
    
    return best

def _verbose_statistics_printer(
    analyte: str = None, 
    best_stddev: float = None, 
    best_avg: float = None, 
    best_wells: list[Well] = None):
        # Formatting for printing
        analyte_name = str(analyte).ljust(4)
        stddev_print = str(round(best_stddev, 3)).rjust(7)
        avg_print = str(round(best_avg,2)).rjust(7)
        percent_std_dev = round((abs(best_stddev) / abs(best_avg)) * 100, 2)
        best_wells_str = ' '.join([str(t.parent_scanfile.name[:9]) + " " + t.name for t in best_wells])
        nSpectra = len(best_wells)

        # Colors for highlighting certain bad things
        if abs(best_avg) < 15:
            avg_print = f'{bcolors.WARNING}{avg_print}{bcolors.ENDC}'
        
        
        if abs(percent_std_dev) > 8 and abs(percent_std_dev) < 15:
            percent_std_dev = f'{bcolors.WARNING}{str(percent_std_dev).rjust(7) + "%"}{bcolors.ENDC}'
        elif abs(percent_std_dev) > 15:
            percent_std_dev = f'{bcolors.FAIL}{str(percent_std_dev).rjust(7) + "%"}{bcolors.ENDC}'
        else:
            percent_std_dev = str(percent_std_dev).rjust(7) + '%'


        print(f'{analyte_name}:\tstddev: {stddev_print}\t\tavg: {avg_print}\trel_stddev: {percent_std_dev}\tnSpectra: {nSpectra}\tBest Wells: {best_wells_str}')


if __name__ == "__main__":
    e1 = EKKOScanSummary('./data/AAB_1023_summary.cdxs')
    spectra1 = e1.get_CD_per_absorbance('A3')

    e2 = EKKOScanSummary('./data/AAB_1019_summary.cdxs')
    spectra2 = e2.get_CD_per_absorbance('A1')

    e3 = EKKOScanSummary('./data/AAB_1024_summary.cdxs')
    spectra3 = e3.get_CD_per_absorbance('A5')

    dif = CalculateAvgSpectra([spectra1, spectra2, spectra3])

    PickN([spectra1, spectra2, spectra3])

    PlotMultipleSpectra([spectra1, spectra2, spectra3], ylimits=[-100,-140])
