import pandas as pd
from itertools import combinations
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .EKKOScanFormats import EKKOScanSummary, Well
from .utilities import GetAllSpectraFromWells
from .utilities import bcolors, SpectraType

def CalculateStdSpectra(
    spectra: list[dict], 
    wl: int = 520, 
    spectra_type: SpectraType = None) -> float:
    '''
    For a list of spectra, calculate the std deviation for a given wavelength.
    
    Can be used on spectra (dictionaries with wavelengths as keys and intensities as values) directly
    or on Well objects from EKKO tools. If using well objects, the requested spectra_type (cd, abs, or cd_per_abs
    must be requested
    '''

    if spectra_type == None:
        if not all([isinstance(s, dict) for s in spectra]):
            raise TypeError(f'Spectra type was {spectra_type} but not all items in spectra list were dicts')
    else:
        if not all([isinstance(s, Well) for s in spectra]):
            raise TypeError(f'Spectra type was {spectra_type} but not all items in spectra list were Well objects')
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['std'].to_dict()[str(wl)]

def CalculateAvgSpectra(
    spectra: list[dict], 
    wl: int = 520, 
    spectra_type = None) -> float:
    
    '''
    For a list of spectra, calculate the average intensity value for a given wavelength.
    
    Can be used on spectra (dictionaries with wavelengths as keys and intensities as values) directly
    or on Well objects from EKKO tools. If using well objects, the requested spectra_type (cd, abs, or cd_per_abs
    must be requested
    '''

    if spectra_type == None:
        if not all([isinstance(s, dict) for s in spectra]):
            raise TypeError(f'Spectra type was {spectra_type} but not all items in spectra list were dicts')
    else:
        if not all([isinstance(s, Well) for s in spectra]):
            raise TypeError(f'Spectra type was {spectra_type} but not all items in spectra list were Well objects')
        spectra = GetAllSpectraFromWells(spectra, spectra_type=spectra_type)

    df = pd.DataFrame(spectra)
    return df.describe().transpose()['mean'].to_dict()[str(wl)]

def PickN(
    l: list[Well], 
    n = 2, 
    wl = 520, 
    spectra_type: SpectraType = None, 
    verbose = False) -> tuple[Well]:
    '''
    Picks the n-closest spectra in a list at some wavelength by calculating the lowest
    standard deviation of the spectra at the selected wavelength.
    
    Parameters
    ----------
    l: list[Well]
        List which contains the EKKOTools.EKKOScanFormats.Well objects

    n: int
        Number of spectra which are to be selected

    wl: float
        Wavelength at which the standard deviation is to be calculated

    spectra_type: SpectraType
        'cd', 'abs', or 'cd_per_abs'

    verbose: Bool
        Prints the details of the spectrum selection process

    Returns
    ----------
    best: iterable[Well]
        The n-number of spectra which provide the lowest standard deviation 
    '''
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

def PCAWells(
    wells: list[Well], 
    n_comp: int = 3, 
    spectra_type: str = 'cd_per_abs', 
    umap = False, 
    scale = True) -> None:
    '''
    Performs PCA on the spectral data
    '''
    dfs = []

    for well in wells:
        if spectra_type.casefold() == 'cd':
            spectrum = well.CD

        elif spectra_type.casefold() == 'abs':
            spectrum = well.ABS

        elif spectra_type.casefold() == 'cd_per_abs':
            spectrum = well.CD_PER_ABS

        else:
            raise Exception('Only CD, ABS, and CD_per_ABS are acceptable spectral types')

        wls = [f"WL_{x}" for x in spectrum.keys()]
        data = [float(x) for x in spectrum.values()]
        df = pd.DataFrame([wls, data]).transpose().rename(columns={1:f'{well.analyte}'}).set_index(0).transpose()
        dfs.append(df)

    x = pd.concat(dfs)

    if scale:
        scaler = StandardScaler()
        x[x.columns] = scaler.fit_transform(x[x.columns])

    if umap:
        from umap import UMAP
        transformer = UMAP(n_components=n_comp)
        labels = [f"UMAP_{x + 1}" for x in range(n_comp)]
    else:
        labels = [f"PC{x + 1}" for x in range(n_comp)]
        transformer = PCA(n_components=n_comp)

    
    return pd.DataFrame(transformer.fit_transform(x), columns=labels, index=x.index) #columns=labels

def _verbose_statistics_printer(
    analyte: str = None, 
    best_stddev: float = None, 
    best_avg: float = None, 
    best_wells: list[Well] = None):
    '''
    Prints formatted text for the PickN function if given an analyte name, best standard deviation
    '''
    # Formatting for printing
    analyte_name = str(analyte).ljust(4)
    stddev_print = str(round(best_stddev, 3)).rjust(7)
    avg_print = str(round(best_avg,2)).rjust(7)
    percent_std_dev = round((abs(best_stddev) / abs(best_avg)) * 100, 2)
    best_wells_str = ' '.join([str(t.parent_scanfile.name[:9]) + " " + t.name for t in best_wells])
    nSpectra = len(best_wells)

    # If the avg CD value is low, warning
    if abs(best_avg) < 15:
        avg_print = f'{bcolors.WARNING}{avg_print}{bcolors.ENDC}'
    
    # Percent stddev
    if abs(percent_std_dev) > 8 and abs(percent_std_dev) < 15:
        percent_std_dev = f'{bcolors.WARNING}{str(percent_std_dev).rjust(7) + "%"}{bcolors.ENDC}'
    elif abs(percent_std_dev) > 15 or str(percent_std_dev) == 'nan':
        percent_std_dev = f'{bcolors.FAIL}{str(percent_std_dev).rjust(7) + "%"}{bcolors.ENDC}'
    else:
        percent_std_dev = f'{bcolors.OKGREEN}{str(percent_std_dev).rjust(7)}%{bcolors.ENDC}'

    # Print formatted string
    print(f'{analyte_name}:\tstddev: {stddev_print}\t\tavg: {avg_print}\trel_stddev: {percent_std_dev}\tnSpectra: {nSpectra}\tBest Wells: {best_wells_str}')
