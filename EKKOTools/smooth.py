from scipy.signal import savgol_filter
from .EKKOScanFormats import Well

from numpy.linalg import LinAlgError

def SmoothWellSpectra(
    well: Well, 
    window_length: int, 
    polyorder: int) -> Well:
    '''
    Smooths all spectra in a well and stores them in the 
    spectrum attributes (CD, ABS, and CD_PER_ABS)

    Parameters
    ----------
    well: Well
        Well object which has the get_CD(), get_abs(), and get_CD_per_abs() methods

    window_length: int
        Number of side points to use for the Savitzky-Golay filter

    polyorder: float
        Order of the low-degree smoothing polynomial for the Savitzky-Golay filter

    Returns
    ----------
    well: Well
        The same well which was passed to the function but with the modified
        attributes. This return value is technically unnecessary because you
        could just use this function to modify the spectral attributes of the
        Well object directly.
    '''

    cd = well.get_CD()
    abs = well.get_abs()
    cd_per_abs = well.get_CD_per_abs()

    # Get the wavelengths
    keys = cd.keys()

    cd = [float(x) for x in cd.values()]
    abs = [float(x) for x in abs.values()] 
    cd_per_abs = [float(x) for x in cd_per_abs.values()]

    well.CD = dict(zip(keys, savgol_filter(
        cd, 
        window_length=window_length, 
        polyorder=polyorder)))

    try:
        well.ABS = dict(zip(keys, savgol_filter(
            abs, 
            window_length=window_length, 
            polyorder=polyorder)))
    except LinAlgError:
        print(f"Could not smooth absorbance for {well.parent_scanfile} well {well.name}")

    try:
        well.CD_PER_ABS = dict(zip(keys, savgol_filter(
            cd_per_abs, 
            window_length=window_length, 
            polyorder=polyorder)))
    except LinAlgError:
        print(f"Could not smooth CD_PER_ABS for {well.parent_scanfile} well {well.name}")

    return well
