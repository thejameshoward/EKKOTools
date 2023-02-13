# EKKOTools
## Spectrum analysis and tools for the EKKO CD Platereader
<br>

`EKKOTools` is a package which provides useful tools for ingesting and analyzing the summary scan files produced by the EKKO CD Microplate Reader

## Installation
Clone the repository and cd into the root directory which contains setup.py

    cd EKKOTools/
    pip install .



## Usage
`EKKOTools` reads the information from the "Well Info:" table at the bottom of scan summary files. This can be an easy way to map analyte names to the well, and doing so unlocks a number of features within `EKKOTools` like collecting all scans of a particular analyte from a large directory filled with scan summary files.

You can overwrite the Well:information assigment as well. `EKKOTools` uses a secondary file called a scan key which is an xlsx or csv spreadsheet.

The data folder should look something like this

    EKKOTools/data/JRH_2098_summary.cdxs
    EKKOTools/data/JRH_2098_summary_scan_key.csv
    EKKOTools/data/JRH_2101_summary.cdxs
    EKKOTools/data/JRH_2101_summary_scankey.xlsx

If you are using scan keys, they should be formatted like so

    A1,R-methylbenzylamine
    A2,S-methylbenzelamine
    A3,analyte3
    ...

<br>
Then run the following code to see if all of your data is ingested correctly.

<br>

    ss = GetAllEKKOScanSummaries(Path('./examples/data/'))
        
    for s in ss:
        for well in s.wells:
            print(f'{s.name.ljust(25)}\t{well.name}\t{well.analyte}')

<br>

## Selecting similar spectra and finding the average
To get the average of 3 spectra which are closest, we calculate the relative standard deviation between all combinations of the spectra. The lowest relative std. dev. are the spectra which are selected with the `PickN` function. These spectra are then averaged and plotted.

    # Find the data files
    ss = GetAllEKKOScanSummaries(Path('./examples/data/'))
        
    # Get all of the Wells of a particular analyte
    wells = GetAllWells(ss, analyte='IH5)

    # Pick the 3 closest Wells at the wavelength 520 nm
    wells = PickN(l = wells, n = 3, wl = 520, spectra_type = 'CD_per_abs')

    # Get the average of Wells
    avg = GetAverageWell(wells)

    # Plot the CD, ABS, and G-factor spectra of the average well
    PlotAllSpectra(avg, title="Average Spectra of IH5")