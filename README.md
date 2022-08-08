# EKKOTools
## Spectrum analysis and tools for the EKKO CD Platereader
<br>

`EKKOTools` is a package which provides useful tools for ingesting and analyzing the summary scan files produced by the EKKO CD Microplate Reader

## Installation
Install the package using pip. Make sure you are in the parent directory of the project (the one that contains the setup.py)

    pip install .



## Usage
`EKKOTools` uses a secondary file called a scan key which is a simple xlsx or csv spreadsheet that maps wells to particular analytes. This feature is optional, but if you want to use all the features of `EKKOTools`, the analytes must be mapped to the wells.

The data folder should look something like this

    EKKOTools/data/JRH_2098_summary.cdxs
    EKKOTools/data/JRH_2098_summary_scan_key.csv
    EKKOTools/data/JRH_2101_summary.cdxs
    EKKOTools/data/JRH_2101_summary_scankey.xlsx

<br>

    ss = GetAllEKKOScanSummaries(Path('./data/'))
        
    for s in ss:
        for well in s.wells:
            print(f'{s.name.ljust(25)}\t{well.name}\t{well.analyte}')

<br>
The behavior of this program when the product of `PYMP_NUM_THREADS` and `nprocs` is greater than the number of available CPU cores of the host machine is unknown.
<br>
<br> 

## Current Limitations
`CRESTPy` does not handle charged molecules. <br>
`CRESTPy` will only return conformers which are energy minima (whether local or global). Transition state structures between conformations are not found. <br>
`CRESTPy` currently returns conformers within 6 kcal/mol of the ground state.<br>
`CREST` output using SDF files will not return the energy <br>
`CRESTPy` 


## Future Features
Conformer sorting<br>
Conformer energy window expanded beyond 6kcal/mol <br>
