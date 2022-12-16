from .EKKOScanFormats import Well, EKKOScanSummary
from pathlib import Path
from enum import Enum
import pandas as pd

import copy

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

class SpectraType(Enum):
    CD = 'cd'
    ABS = 'abs'
    CD_PER_ABS = 'cd_per_abs'

def GetSpectrumDifferencesWells(
    w1: Well,
    w2: Well,
    compare: SpectraType = SpectraType.CD) -> dict:
    '''
    Gets the difference of some property the CD spectra of two EKKO formatted wells. 
    
    Compare: str
    values can be CD, CD_per_abs, or ABS
    '''

    if compare.casefold() == 'cd':
        cd1 = w1.get_CD()
        cd2 = w2.get_CD()
        return {x: cd1[x] - cd2[x] for x in cd1 if x in cd2}

    elif compare.casefold() == 'abs':
        abs1 = w1.get_abs()
        abs2 = w2.get_abs()
        return {x: abs1[x] - abs2[x] for x in abs1 if x in abs2}

    elif compare.casefold() == 'cd_per_abs':
        cd_per_abs_1 = w1.get_CD_per_abs()
        cd_per_abs_2 = w2.get_CD_per_abs()
        return {x: cd_per_abs_1[x] - cd_per_abs_2[x] for x in cd_per_abs_1.keys() if x in cd_per_abs_2.keys()}

    else:
        raise Exception

def GetDifferenceWell(
    w1: Well,
    w2: Well) -> Well:
    '''
    returns w1 - w2
    Gets a well which posesses spectral attributes (CD, absorbance, cd_per_abs)
    which are the difference between the two input wells 
    
    Compare: str
    values can be CD, CD_per_abs, or ABS
    '''

    # Make a new copy of the well
    n = copy.deepcopy(w1)
    
    # Change the analyte
    n.analyte = f'{w1.analyte} - {w2.analyte}'

    cd1 = w1.CD
    cd2 = w2.CD
    n.CD = {x: cd1[x] - cd2[x] for x in cd1 if x in cd2}

    abs1 = w1.ABS
    abs2 = w2.ABS
    n.ABS = {x: abs1[x] - abs2[x] for x in abs1 if x in abs2}

    cd_per_abs_1 = w1.CD_PER_ABS
    cd_per_abs_2 = w2.CD_PER_ABS
    n.CD_PER_ABS = {x: cd_per_abs_1[x] - cd_per_abs_2[x] for x in cd_per_abs_1.keys() if x in cd_per_abs_2.keys()}

    return n

def GetAllEKKOScanSummaries(p: Path) -> list[EKKOScanSummary]:
    '''
    Returns all EKKOScanSummaries in a directory
    '''
    if not isinstance(p, Path):
        p = Path(p)
    if not p.is_dir():
        raise NotADirectoryError('Can only find scan summaries within a directory')

    return [EKKOScanSummary(x) for x in p.glob('*.cdxs')]

def GetSignalRatio(
    well: Well, 
    wavelength_1: float, 
    wavelength_2: float,
    spectra_type: str = 'cd'
    ) -> float:
    '''
    Given a Well and two wavelengths, calculates the ratio of wavelength_1 to 
    wavelength_2
    '''
    #TODO Get all of this conditional/string interpretation out of here.
    if spectra_type.casefold() == 'cd':
        spectrum = well.get_CD()
    elif spectra_type.casefold() == 'abs':
        spectrum = well.get_abs()
    elif spectra_type.casefold() == 'cd_per_abs':
        spectrum = well.get_CD_per_abs()

    return float(spectrum[str(wavelength_1)]) / float(spectrum[str(wavelength_2)])

def GetAllSpectraFromWells(
    wells: list[Well] = None, 
    spectra_type = 'cd',
    all_same_analyte = True) -> list[dict]:
    '''
    Given a list of wells of the same analyte, return a list of spectra dictionaries.
        
    The list of wells are checked to ensure they have the same analyte. The return
    list of spectral dictionaries have the wavelengths as the keys and the intenisties
    as the values
    ''' 

    if not isinstance(wells, list) and not isinstance(wells, tuple):
        wells = [wells]

    # I can't remember why I wanted to limit this function to just a single analyte, but now theres an option to not
    if all_same_analyte:
        if len(set([x.analyte for x in wells])) != 1:
            raise Exception("All wells must have the same analyte")

    spectra = []

    for well in wells:

        if spectra_type.casefold() == 'cd':
            spectrum = well.CD

        elif spectra_type.casefold() == 'abs':
            spectrum = well.ABS

        elif spectra_type.casefold() == 'cd_per_abs':
            spectrum = well.CD_PER_ABS

        else:
            raise Exception('Only CD, ABS, and CD_per_ABS are acceptable spectral types')

        spectra.append(spectrum)

    return spectra

def GetAllWells(
    scan_summaries: list = None,
    analyte: str = '') -> list[Well]:
    '''Searches through all scan summaries for wells with a particular analyte'''
    wells = []
    for summary in scan_summaries:
        for well in summary.wells:
            if well.analyte == analyte:
                wells.append(well)
    return wells

def GetAllAnalytes(folder: Path) -> set[str]:
    '''
    Gets all of the analytes of all the scan summaries in 
    the provided directory. Returns a set of strings 
    of all analyte names.
    '''
    if not isinstance(folder, Path):
        folder = Path(folder) # Eventually this should be a try/except but I don't know what exceptions we'll have
        if not folder.is_dir():
            raise ValueError(f'{folder} is not a directory.')

    analytes = set()
    ss = GetAllEKKOScanSummaries(folder)

    for summary in ss:
        for well in summary.wells:
            analytes.add(well.analyte)

    return analytes

def WriteWellsToXLSX(
    wells: list[Well], 
    filename: Path) -> None:
    '''
    Writes the well spectra to a nicely formatted XLSX file
    '''

    assert(filename.suffix == '.xlsx')

    wavelengths = [float(x) for x in wells[0].CD.keys()]

    df = pd.DataFrame({'WAVELENGTHS':wavelengths})

    for well in wells:
        df[f'CD_{well.name}'] = well.CD.values()
    for well in wells:
        df[f'ABS_{well.name}'] = well.ABS.values()

    df.to_excel(filename, index=False)

def GetAverageWell(wells: list[Well]) -> Well:
    '''
    Creates Well object with the average CD, ABS, and CD_PER_ABS
    of the input Wells.
    '''
    if len(set([x.analyte for x in wells])) != 1:
        raise Exception("All wells must have the same analyte")
    analyte_name = wells[0].analyte

    cds = pd.DataFrame([x.CD for x in wells]).transpose().mean(axis=1)
    absorbances = pd.DataFrame([x.ABS for x in wells]).transpose().mean(axis=1)

    #TODO Change hardcoded column names to accomodate different units
    # Get dataframe with the CD and the ABS values
    df = pd.concat([cds, absorbances], axis=1)
    df.columns = ['CD-mDeg', 'ABS']

    # Add the wavelengths
    df.insert(0, column='WL', value=df.index.to_list())

    # Put it in the strange format which the Well object requires
    #TODO Handing a specifically formatted dataframe to Well is inflexible
    data_row = pd.DataFrame(dict(zip(['WL', 'CD-mDeg', 'ABS'], [['Average'], ['NaN'], ['Nan']])))
    df = pd.concat([data_row, df], axis=0)

    return Well(df, parent_scanfile=None, analyte_name=analyte_name)

#TODO
def MakeCalibrationCurve():
    pass