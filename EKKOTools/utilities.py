from EKKOTools.EKKOScanFormats import Well, EKKOScanSummary
from pathlib import Path

def GetSpectrumDifferencesWells(
    w1: Well,
    w2: Well,
    compare = 'cd') -> dict:
    '''Gets the difference of some property the CD spectra of two EKKO formatted wells. 
    
    Compare: str
    values can be CD, CD_per_abs, or ABS'''

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

def GetAllEKKOScanSummaries(p: Path) -> list[EKKOScanSummary]:
    '''Returns all EKKOScanSummaries in a directory'''
    assert(p.is_dir())
    return [EKKOScanSummary(x) for x in p.glob('*.cdxs')]

def FixScanKeys(p: Path):
    '''Fixes the scan keys to be csv files'''
    pass

def GetAllSpectraFromWells(
    wells: list[Well] = None, 
    spectra_type = 'cd',
    all_same_analyte = True) -> list[dict]:
    '''Given a list of wells of the same analyte, return a list of spectra dictionaries.
        
        The list of wells are checked to ensure they have the same analyte. The return
        list of spectral dictionaries have the wavelengths as the keys and the intenisties
        as the values''' 

    # I can't remember why I wanted to limit this function to just a single analyte, but now theres an option to not
    if all_same_analyte:
        try:
            analytes = [q.analyte for q in wells]
            assert(all(analytes[0] == x for x in analytes))
        except:
            raise ValueError('All analytes must be identical')

    spectra = []

    for well in wells:

        if spectra_type.casefold() == 'cd':
            spectrum = well.get_CD()

        elif spectra_type.casefold() == 'abs':
            spectrum = well.get_abs()

        elif spectra_type.casefold() == 'cd_per_abs':
            spectrum = well.get_CD_per_abs()

        else:
            raise Exception('Only CD, ABS, and CD_per_ABS are acceptable spectral types')

        spectra.append(spectrum)

    return spectra

def GetAllWells(
    scan_summaries: list = None,
    analyte: str = '') -> list[dict]:
    '''Searches through all scan summaries for wells with a particular analyte'''
    wells = []
    for summary in scan_summaries:
        for well in summary.wells:
            if well.analyte == analyte:
                wells.append(well)
    return wells

def GetAllAnalytes(folder: Path) -> list[str]:
    '''Gets all of the analytes of all the scan summaries in 
        the provided directory. Returns a set of all analytes'''
    if not isinstance(folder, Path):
        folder = Path(folder) # Eventually this should be a try/except but I don't know what exceptions we'll have
    assert(folder.is_dir())

    analytes = set()
    ss = GetAllEKKOScanSummaries(folder)

    for summary in ss:
        for well in summary.wells:
            analytes.add(well.analyte)

    return analytes

if __name__ == "__main__":
    p = Path('./data/')
    print(p.absolute())
    print(GetAllAnalytes(p))