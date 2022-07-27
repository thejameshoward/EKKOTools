from multiprocessing.sharedctypes import Value
from typing import Type
import pandas as pd
import re
import numpy as np
from pathlib import Path

possible_wells = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1',
                  'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                  'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',
                  'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4',
                  'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5',
                  'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',
                  'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7',
                  'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
                  'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',
                  'A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10',
                  'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11',
                  'A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'G12', 'H12']


class Well():  
    def __init__(self, df: pd.DataFrame, parent_scanfile: str,  analyte_name = None):
        self.df = df.reset_index()
        if not self.df["WL"][0] in possible_wells:
            raise ValueError("Well format not understood")
        else:
            self.name = self.df["WL"][0]
            self.parent_scanfile = parent_scanfile
            self.df = self.df.drop(0)
            self.df = self.df.set_index("WL")
            self.__analyte = analyte_name

    @property
    def analyte(self):
        return self.__analyte

    @analyte.setter
    def analyte(self, analyte_name: str) -> None:
        self.__analyte = analyte_name

    def get_CD(self) -> dict:
        return {
            wl: float(self.df["CD-mDeg"][wl])
            for wl in self.df.index
        }

    def get_abs(self) -> dict:
        return {
            wl: float(self.df["ABS"][wl])
            for wl in self.df.index
        }

    def get_CD_per_abs(self) -> dict:
        '''Returns the CD divided by the ABS at all wavelengths (aka g-factor)'''
        abs = self.get_abs()
        cd = self.get_CD()
        return {wl: float(cd[wl] / abs[wl]) for wl in self.df.index}

class EKKOScanSummary():
    def __init__(self, file: Path):

        if not isinstance(file, Path):
            file = Path(file)
            if file.is_dir():
                raise ValueError(f"Path handed to EKKOScanSummary is a directory, not a dir!")

        self.file = file

        if self.file.suffix == ".cdxs" or ".CDXS":
            self.content = pd.read_csv((self.file), header = None)
            self.content = self.content[0].str.split('\t', expand=True)
            if self.content[0][0] != "Hinds Instruments CD Reader":
                raise ValueError(f"The file {self.file.name} is not formatted like a EKKO CD Wellplate Reader cdxs file")
        else:
            raise ValueError(f"The file {self.file.name} is not a cdxs file")

        if self._has_scan_key():
            self.wells = self._assign_wells_from_scan_key()
        else:
            self.wells = [Well(scan, self.file) for scan in self.scan_list]

        self.name = Path(self.content[0][2]).stem
        self.date = self.content[0][1].split('   ')[0]
        self.time = self.content[0][1].split('   ')[1]
        self.scan_process = self.content[0][4]
        self.well_plate_type = self.content[1][9]

    @property
    def blocksize(self):
        '''Length of the well scans which is 1 for each wavelength plus the well label (A1, A2, H3, etc...)'''
        digits = re.findall(r'\b\d+\b', self.content[0][4])
        block_size = (int(digits[1]) - int(digits[0])) / int(digits[2]) + 2
        return int(block_size)

    @property
    def scandata(self):
        '''Raw scan data which is not split'''
        df = pd.read_csv(self.file, skiprows=11, delimiter="\t", on_bad_lines='warn', usecols=["WL", "CD-mDeg", "ABS"])
        df.drop(df.tail(17).index, inplace=True)
        return df

    @property
    def scan_list(self):
        scan_list = np.array_split(self.scandata, len(
            self.scandata["WL"])/self.blocksize)
        return scan_list

    def get_wavelengths(self):
        # Extracts wavelengths from first well plate reading. Assumes all wells measured same WL
        wavelengths = self.scandata["WL"][1:self.blocksize]
        return wavelengths

    def get_wells(self):
        first_column = self.content[0][12:] # These array positions are hard coded, so they may have to be changed
        wells = []
        for row in first_column:
            if row in possible_wells:
                wells.append(row)
            else:
                pass
        return wells

    def get_specific_well(self, well_label: str = None) -> Well:
        '''Returns the first Well object of the EKKOScanSummary which has the name well_label'''
        assert(well_label in possible_wells)

        for well in self.wells:
            if well.name == well_label:
                return well

    def get_wells_of_particular_analytes(self, analyte: str = None) -> list:
        '''Returns all well objects whose analyte matches the input analyte string'''
        return [x for x in self.wells if x.analyte == analyte]

    def get_CD(self, well_name):
        '''Pass in string containing well name (A1 or H11) to get CD of a particular well'''
        for well in self.wells:
            if well.name == well_name:
                return well.get_CD()
        raise ValueError("Well {} not found".format(well_name))

    def get_CD_per_absorbance(self, well_name: str):
        for well in self.wells:
            if well.name == well_name:
                return well.get_CD_per_abs()
        raise ValueError("Well {} not found".format(well_name))

    def _has_scan_key(self):
        '''Attempts to find a scan_key document which named experiment_summary_scan_key.csv'''
        p = Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scan_key.csv'))
        if p.exists():
            self._scan_key = p
            return True
        else:
            p = Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scan_key.xlsx'))
            if p.exists():
                self._scan_key = p
                return True
            else:
                return False        

    def _assign_wells_from_scan_key(self):
        '''Attempts to pull data about the scan file from a second file labeled experiment_summary_scan_key.csv. Can also be xlsx file'''

        if self._scan_key.suffix == '.csv':
            analyte_map = pd.read_csv(self._scan_key, header = None).set_index(0)[1].to_dict()
        elif self._scan_key.suffix == '.xlsx':
            analyte_map = pd.read_excel(self._scan_key, header = None).set_index(0)[1].to_dict()
        else:
            raise TypeError('Scan key file format not recognized')

        local_wells = [Well(scan, self.file) for scan in self.scan_list]

        for well in local_wells:
            if well.name in analyte_map.keys():
                well.analyte = analyte_map[well.name]

        return local_wells



if __name__ == "__main__":
    from pprint import pprint
    
    v = EKKOScanSummary(Path('./data/ZA_1014-1015_summary.cdxs'))


    for w in v.wells:
        pprint(w.get_CD_per_abs())

    print(v.get_wells())
    print(f'FILE: {v.file}')
    print(f'DATE: {v.date}')
    print(f'TIME: {v.time}')
    print(f'NAME: {v.name}')
    print(f'SCAN_PROCESS: {v.scan_process}')
    print(f'WELL PLATE TYPE: {v.well_plate_type}')

    for w in v.wells:
        print(f'WELL: {w.name}    ANALYTE: {w.analyte}')

    
