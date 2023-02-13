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
    BOLD = '\033[1m'
    ENDC = '\033[0m'

#TODO Change implementation so that SpectraType is used to distinguish spectra
class SpectraType(Enum):
    CD = 'cd'
    ABS = 'abs'
    CD_PER_ABS = 'cd_per_abs'

def _getSpectrumDifference(
    d1: dict,
    d2: dict,
    compare: SpectraType = SpectraType.CD) -> dict:
    '''
    Calculates the difference between two spectra which are formatted
    as dictionaries. The dictionary keys are the wavelengths which
    are measured in the spectrum and the values are the intensities
    of the spectral signal.
    
    Parameters
    ----------
    d1: dict
        Dictionary with the wavelengths as keys and the spectral signal
        as its values.

    d2: dict
        Dictionary with the wavelengths as keys and the spectral signal
        as its values.

    Returns
    ----------
    dict
    '''
    # Check the dictionaries are equal
    #TODO Add support for unequal length measurements (i.e., change of method in EKKO spectrometer)
    if d1.keys() != d2.keys():
        raise ValueError('Spectra must be measured have equal wavelengths measured.')

    return {x: d1[x] - d2[x] for x in d1 if x in d2}


def getSpectrumSum(
    d1: dict,
    d2: dict,
    compare: SpectraType = SpectraType.CD) -> dict:
    '''
    Calculates the sum between two spectra which are formatted
    as dictionaries. The dictionary keys are the wavelengths which
    are measured in the spectrum and the values are the intensities
    of the spectral signal.
    
    Parameters
    ----------
    d1: dict
        Dictionary with the wavelengths as keys and the spectral signal
        as its values.

    d2: dict
        Dictionary with the wavelengths as keys and the spectral signal
        as its values.

    Returns
    ----------
    dict
    '''
    # Check the dictionaries are equal
    #TODO Add support for unequal length measurements (i.e., change of method in EKKO spectrometer)
    if d1.keys() != d2.keys():
        raise ValueError('Spectra must be measured have equal wavelengths measured.')

    return {x: d1[x] + d2[x] for x in d1 if x in d2}

def GetDifferenceWell(
    w1: Well,
    w2: Well) -> Well:
    '''
    Calculates the well which posesses spectral attributes (CD, absorbance, cd_per_abs)
    which are the difference between the two input wells (well 1 - well 2)
    
    Parameters
    ----------
    w1: Well
        Well object which has the CD, ABS, and CD_PER_ABS properties

    w2: Well
        Well object which has the CD, ABS, and CD_PER_ABS properties

    Returns
    ----------
    newWell: Well
        A Well object with the difference between the spectral attributes
        CD, ABS, and CD_PER_ABS
    '''

    # Make a new copy of the well
    newWell = copy.deepcopy(w1)
    
    # Change the analyte
    newWell.analyte = f'{w1.analyte} - {w2.analyte}'

    cd1 = w1.CD
    cd2 = w2.CD
    #newWell.CD = {x: cd1[x] - cd2[x] for x in cd1 if x in cd2}
    newWell.CD = _getSpectrumDifference(cd1,cd2)

    abs1 = w1.ABS
    abs2 = w2.ABS
    newWell.ABS = _getSpectrumDifference(abs1,abs2)

    cd_per_abs1 = w1.CD_PER_ABS
    cd_per_abs2 = w2.CD_PER_ABS
    newWell.CD_PER_ABS = _getSpectrumDifference(cd_per_abs1, cd_per_abs2)

    return newWell

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
            spectra.append(well.CD)

        elif spectra_type.casefold() == 'abs':
            spectra.append(well.ABS)

        elif spectra_type.casefold() == 'cd_per_abs':
            spectra.append(well.CD_PER_ABS)

        else:
            raise Exception('Only CD, ABS, and CD_per_ABS are acceptable spectral types')

    return spectra

def GetAllWells(
    scan_summaries: list = None,
    analyte: str = '') -> list[Well]:
    '''
    Finds all the Well objects within a list of EKKOScanSummary objects
    that possess an analyte property (Well.analyte) which is equal to the
    analyte string passed to the funciton.
    
    Parameters
    ----------
    scan_summaries: list[EKKOScanSummary]
        List of EKKOScanSummary objects which is to be searched

    analyte: str
        Name of the analyte of interest

    Returns
    ----------
    wells: list[Well]
        A list of Well objects which possess the <analyte> str
    '''

    # Check if a single EKKOScanSummary was passed
    if isinstance(scan_summaries, EKKOScanSummary):
        scan_summaries = [scan_summaries]

    wells = []

    for summary in scan_summaries:
        for well in summary.wells:
            if well.analyte == analyte:
                wells.append(well)
    return wells

def GetAllAnalytes(folder: Path) -> set[str]:
    '''
    Finds all the Well objects within a list of EKKOScanSummary objects
    that possess an analyte property (Well.analyte) which is equal to the
    analyte string passed to the funciton.
    
    Parameters
    ----------
    folder: Path
        Folder which contains the datafiles from the EKKO spectrometer

    Returns
    ----------
    analytes: set
        A set of all analyte strings
    '''
    # If given a single EKKOScanSummary, return all the analytes
    if isinstance(folder, EKKOScanSummary):
        return set([x.analyte for x in folder.wells])

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

    Get's the well which has the average CD, ABS, and 
    CD_PER_ABS of the input wells.

    Parameters
    ----------
    wells: list[Well]
        List of Well objects which will be averaged

    Returns
    ----------
     Well
        The average well of all the input wells

    '''
    if len(set([x.analyte for x in wells])) != 1:
        raise Exception("All wells must have the same analyte")
        
    analyte_name = wells[0].analyte  + '_avg'

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

def DetermineLambdaMaxRange(well: Well, range: list[float, float]) -> float:
    '''
    Given a well, determine the lambda max (wavelength)
    within a certain range
    '''
    possible_wl = [x for x in well.CD.keys() if float(x) <= range[1] and float(x) >= range[0]]

    # Changed to include abs() function for negative CD spectra
    results = {p: abs(well.CD[p]) for p in possible_wl}

    return max(results, key=results.get) 


#TODO
def MakeCalibrationCurve():
    raise NotImplementedError