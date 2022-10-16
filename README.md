# EKKOTools
## Spectrum analysis and tools for the EKKO CD Platereader
<br>

`EKKOTools` is a package which provides useful tools for ingesting and analyzing the summary scan files produced by the EKKO CD Microplate Reader

## Installation
Clone the repository and cd into the root directory which contains setup.py

    cd EKKOTools/
    pip install .



## Usage
`EKKOTools` uses a secondary file called a scan key which is a simple xlsx or csv spreadsheet that maps wells to particular analytes. This feature is optional, but if you want to use all the features of `EKKOTools`, the analytes must be mapped to the wells.

The data folder should look something like this

    EKKOTools/data/JRH_2098_summary.cdxs
    EKKOTools/data/JRH_2098_summary_scan_key.csv
    EKKOTools/data/JRH_2101_summary.cdxs
    EKKOTools/data/JRH_2101_summary_scankey.xlsx

Each scan key should be formatted like so

    A1,R-methylbenzylamine
    A2,S-methylbenzelamine
    A3,analyte3
    ...

<br>
Then run the following code to see if all of your data is ingested correctly.

<br>

    ss = GetAllEKKOScanSummaries(Path('./data/'))
        
    for s in ss:
        for well in s.wells:
            print(f'{s.name.ljust(25)}\t{well.name}\t{well.analyte}')


<br> 

## Current Limitations and Future Features
`EKKOTools` currently does not read the well labels section of the scan summary cdxs files. A future version will attempt to map the well labels to the EKKOTools.EKKOScanFormats.Well object, which has an attribute "analyte".
