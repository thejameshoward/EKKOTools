
from EKKOTools.EKKOScanFormats import EKKOScanSummary, Well
from EKKOTools.plotting import PlotMultipleSpectra

from itertools import combinations

import pandas as pd
import numpy as np

from EKKOTools.utilities import GetAllSpectraFromWells

def CalculateStdSpectra(spectra: list[dict], wl: int = 520, spectra_type = None) -> float:
    '''For a list of spectra, calculate the average std deviation for a given wavelength'''
    if spectra_type == None:
        for s in spectra:
            assert(isinstance(s, dict))
    else:
        for s in spectra:
            assert(isinstance(s, Well))
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['std'].to_dict()[str(520)]

def CalculateAvgSpectra(spectra: list[dict], wl: int = 520, spectra_type = None) -> float:
    '''For a list of spectra, calculate the average value for a given wavelength'''
    if spectra_type == None:
        for s in spectra:
            assert(isinstance(s, dict))
    else:
        for s in spectra:
            assert(isinstance(s, Well))
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['mean'].to_dict()[str(520)]

def PickN(l: list[Well], n = 2, wl = 520, spectra_type = None, verbose = True) -> tuple:
    '''Picks the n-closest spectra in a list at some wavelength'''
    combos = list(combinations(l, n))

    # Initialize comparison variables with the first combination
    best = combos[0]
    best_std = CalculateStdSpectra(best, spectra_type=spectra_type)

    for combo in combos:
        avg = CalculateAvgSpectra(combo, spectra_type=spectra_type)
        std = CalculateStdSpectra(combo, spectra_type=spectra_type)
        if verbose:
            (f'Number of Spectra: {len(combo)}\tAVG: {round(avg, 2)}\tSTDDEV: {round(std, 2)}')
        if std < best_std:
            best = combo
            best_std = std
    return best


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
