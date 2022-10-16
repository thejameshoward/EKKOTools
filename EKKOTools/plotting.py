import math
import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib

from pathlib import Path

from pprint import pprint

from EKKOTools.EKKOScanFormats import EKKOScanSummary, Well
from EKKOTools.utilities import GetAllSpectraFromWells
#from EKKOTools.JascoScanFile import JascoScanFile

def PruneNAN(data: dict):
    '''Removes values from a dictionary in which the values or the keys are nan'''
    removal = []
    for key, value in data.items():
        if str(key) == 'nan':
            removal.append(key)
            print(key)
        if str(value) == 'nan':
            if key not in removal:
                removal.append(key)
    for r in removal:
        del data[r]
    return data

def PlotSpectrum(
    data: dict, 
    ylimits=None, 
    title=False, 
    plotwavelengths = None, 
    verbose = True,
    **kwargs):
    '''Takes a spectrum as a dict in which keys are the wavelengths and values are the amplitudes'''

    data = PruneNAN(data)

    x, y = list(float(key) for key in data.keys()), list(float(value) for value in data.values())


    print(" should mention that dictionaries also have a method .get() which accepts a default parameter (itself defaulting to None), so that kwargs.get('errormessage') returns the value if that key exists and None otherwise (similarly kwargs.get('errormessage', 17) does what you might think it does). When you don't care about the difference between the key existing and having None as a value or the key not existing, this can be handy.")

    # xlimits
    try:
        xlimits = kwargs.pop('xlimits')
        assert(isinstance(xlimits, list))
        xlim, xlim2 = xlimits[0], xlimits[1]
    except:
        print('xlimits variable not understood, reverting to default x limits')
        xlim, xlim2 = min(x), max(x)

    # Determining ylimits
    try:
        ylimits = kwargs.pop('ylimits')
        assert(isinstance(ylimits, list))
        ylim, ylim2 = ylimits[0], ylimits[1]
    except:
        print('ylimits variable not understood, reverting to default y limits')
        ylim, ylim2 = min(y) + (0.05 * min(y)), max(y) + (0.05 * max(y))



    # Create figure fig and add an axis, ax
    fig_CD, ax_CD = plt.subplots(1)
    plt.axhline(y=0, color='#D1D1D1')
    ax_CD.plot(x, y, color='purple')
    ax_CD.set_ylim(ylim, ylim2)
    ax_CD.set_xlim(xlim, xlim2)
    #plt.xticks(np.arange(xlim, xlim2, 25))

    # Plotwavelengths
    if type(plotwavelengths) == tuple or type(plotwavelengths) == int or type(plotwavelengths) == float:
        d = plotwavelengths
        try:
            for wl in d:
                plt.plot(wl, cd[wl], marker='.', color='red')
                plt.text(wl + (wl * 0.025), data[wl] + (data[wl] * 0.025), "{} nm, {} mDeg".format(
                    str(wl),  # Wavelength
                    str(math.ceil(data[wl]*100)/100)),  # CD rounded up at the second decimal point
                    horizontalalignment='left')
        except(TypeError):
            plt.plot(d, data[d], marker='.', color='red')
            plt.text(d + (d * 0.025), cd[d] + (cd[d] * 0.025), "{} nm, {} mDeg".format(
                str(d),  # Wavelength
                str(math.ceil(cd[d]*100)/100)),  # CD rounded up at the second decimal point
                horizontalalignment='left')

    plt.ylabel("CD (mDeg)")
    plt.xlabel("Wavelength (nm)")

    # Title of the figure
    if title == True:  # By default the name of the scanfile
        plt.title('TITLE EMPTY')
    elif isinstance(title, str):  # If it's a string, use that string as title
        plt.title(title)
    else:
        pass

    plt.show()

def PlotAbsorbance(JascoScanFile, plotwavelengths=None):
    f = JascoScanFile
    absorbance = f.get_abs()
    x, y = list(float(key)
                for key in absorbance.keys()), list(absorbance.values())

    # Wavelengths for scaling X axis
    xlim, xlim2 = min(x), max(x)

    type(xlim)
    type(xlim2)

    fig_ABS, ax_ABS = plt.subplots(1)  # Create figure fig and add an axis, ax
    ax_ABS.plot(x, y, color='blue')
    ax_ABS.set_xlim(xlim, xlim2)
    ax_ABS.plot(x, y)

    # Plotwavelengths
    if type(plotwavelengths) == tuple or type(plotwavelengths) == int or type(plotwavelengths) == float:
        d = plotwavelengths
        try:
            for wl in d:
                plt.plot(wl, absorbance[wl], marker='.', color='red')
                plt.text(wl + (wl * 0.045), absorbance[wl] - (absorbance[wl] * 0.025), "{} nm, {} au".format(
                    str(wl),  # Wavelength
                    str(math.ceil(absorbance[wl]*100)/100)),  # CD rounded up at the second decimal point
                    horizontalalignment='left')
        except(TypeError):
            plt.plot(d, absorbance[d], marker='.', color='red')
            plt.text(d + (d * 0.045), absorbance[d] - (absorbance[d] * 0.025), "{} nm, {} au".format(
                str(d),  # Wavelength
                str(math.ceil(absorbance[d]*100)/100)),  # CD rounded up at the second decimal point
                horizontalalignment='left')

    plt.ylabel("Absorbance (au)")
    plt.xlabel("Wavelength (nm)")
    plt.title(f.name())
    plt.show()

def PlotMultipleSpectra(
    list_of_spectra: list[dict], 
    xlabel = 'Wavelength (nm)',
    ylabel = 'CD (mdeg)',
    ylimits=None, 
    title=False, 
    plotwavelengths=None, 
    xlim: tuple = None):

    # Create figure fig and add an axis, ax
    fig_CD, ax_CD = plt.subplots(1)
    
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if xlim is not None:
        plt.xlim(xlim[0], xlim[1])

    maxy = 0

    for scan_data in list_of_spectra:
        data = PruneNAN(scan_data)

        x, y = list(float(key) for key in data.keys()), list(data.values())

        ax_CD.plot(x, y)

        if max([abs(y_tmp) for y_tmp in y]) >= maxy:
            maxy = max([abs(y_tmp) for y_tmp in y])

    print('YLIMITS HAVE BEEN FIXED WARNING')
    if ylimits is not None:
        plt.ylim(ylimits[0], ylimits[1])

    plt.show()

def PlotAllSpectra(
    wells: list[Well] = [], 
    title = '', 
    xlim: list = None, 
    ylim: list = None, 
    all_same_analyte = True, 
    return_fig = False, 
    **kwargs):       
    '''Plots all the spectra (cd, abs, cd_per_abs) for a list of wells'''

    # Create a subplot with 1 row and 2 columns
    fig, axs = plt.subplots(nrows=1, ncols=3, sharex=True, sharey=False)
    fig.set_size_inches(16, 7)

    plt.suptitle(title)

    axs[0].set_title("CD")
    axs[0].set_xlabel("Wavelength (nm)")
    axs[0].set_ylabel("CD (mdeg)")
    if xlim is not None:
        axs[0].set_xlim(xlim)
    for spectrum in GetAllSpectraFromWells(wells, spectra_type='cd', all_same_analyte=all_same_analyte):
        spectrum = PruneDictionaryKeys(spectrum, xlim) # This is useful for automatically resizing Y-axis to the dataset
        x = [float(t) for t in spectrum.keys()] # This must be done because spectrum.keys() returns strings, not floats for wavelength
        y = [float(z) for z in spectrum.values()]
        axs[0].plot(x,y)

    axs[1].set_title("Absorbance")
    axs[1].set_xlabel("Wavelength (nm)")
    axs[1].set_ylabel("Absorbance")
    if xlim is not None:
        axs[1].set_xlim(xlim)
    for spectrum in GetAllSpectraFromWells(wells, spectra_type='abs', all_same_analyte=all_same_analyte):
        spectrum = PruneDictionaryKeys(spectrum, xlim)
        x = [float(t) for t in spectrum.keys()]
        y = [float(z) for z in spectrum.values()]
        axs[1].plot(x,y)
    
    axs[2].set_title("G-factor")
    axs[2].set_xlabel("Wavelength (nm)")
    axs[2].set_ylabel("CD (mdeg / abs)")
    if xlim is not None:
        axs[2].set_xlim(xlim)
    for spectrum in GetAllSpectraFromWells(wells, spectra_type='cd_per_abs', all_same_analyte=all_same_analyte):
        spectrum = PruneDictionaryKeys(spectrum, xlim)
        x = [float(t) for t in spectrum.keys()]
        y = [float(z) for z in spectrum.values()]
        axs[2].plot(x,y)

    if return_fig:
        return fig, axs

    plt.show()

def PlotAllAbsorbance(
    wells: list[Well] = [], 
    title = '', 
    xlim: list = None, 
    ylim: list = None, 
    all_same_analyte = True):       
    '''
    Plots all the absorbance spectra for a list of wells
    '''
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Absorbance")
    if xlim is not None:
        ax.set_xlim(xlim)
    for spectrum in GetAllSpectraFromWells(wells, spectra_type='cd', all_same_analyte=all_same_analyte):
        spectrum = PruneDictionaryKeys(spectrum, xlim)
        x = [float(t) for t in spectrum.keys()]
        y = [float(z) for z in spectrum.values()]
        ax.plot(x,y)
    
    plt.show()

def PruneDictionaryKeys(d: dict = None, range: list = None):
    '''Removes dictionary keys with float values outside of the accepted range'''
    if range is None:
        return d
    else:
        for k,v in d.copy().items():
            wl = float(k)
            if wl < range[0] or wl > range[1]:
                d.pop(k)
        return d

if __name__ == "__main__":
    file = Path("./data/AAB_1019_summary.cdxs")

    test = EKKOScanSummary(file)

    data = test.get_CD('A1')

    PlotSpectrum(data)
