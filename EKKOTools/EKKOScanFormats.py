import pandas as pd
import re
import numpy as np
from pathlib import Path

# Possible names for wells of a 94 well plate
#TODO Add compatibility for 384 well plates
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

# Added average to possible wells as this indicates
# that a Well was created by averaging multiple wells
# and was not directly measured
possible_wells.append('Average')

class Well():
    '''
    Class for handling information within a well. Instatiation is not done
    directly, but rather from the EKKOScanSummary class which formats the 
    dataframe in a specific way for ingestion by the Well class.
    '''
    def __init__(self, df: pd.DataFrame, parent_scanfile: Path,  analyte_name: str = None):
        self.df = df.reset_index()
        if not self.df["WL"][0] in possible_wells:
            raise ValueError(f"Well format not understood in {parent_scanfile.name}\tWell: {str(self.df['WL'][0])}")
        else:
            self.name = self.df["WL"][0]
            self.parent_scanfile = parent_scanfile
            self.df = self.df.drop(0)
            self.df = self.df.set_index("WL")
            self.__analyte = analyte_name

            # CD attribute which can hold user-defined 
            # spectra which are dictionaries that have 
            # wavelength:intensity key:value pairs
            self.CD = self.get_CD()
            self.ABS = self.get_abs()
            self.CD_PER_ABS = self.get_CD_per_abs()

    @property
    def analyte(self) -> str:
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
    '''
    Class for handling EKKO ScanSummary files (.cdxs).

    Instantiate with a pathlib Path object or string.
    '''
    def __init__(self, file: Path):

        if not isinstance(file, Path):
            file = Path(file)
            if file.is_dir():
                raise ValueError(f"Path handed to EKKOScanSummary is a directory, not a dir!")
            if file.suffix != ".cdxs" or file.suffix != ".CDXS":
                raise ValueError(f"The file {self.file.name} is not formatted like a EKKO CD Wellplate Reader cdxs file")

        self.file = file

        self.content = pd.read_csv((self.file), header = None)
        self.content = self.content[0].str.split('\t', expand=True)

        if self.content[0][0] != "Hinds Instruments CD Reader":
            raise ValueError(f"The file {self.file.name} is not formatted like a EKKO CD Wellplate Reader cdxs file")

        self.name = file.stem
        # Added re.sub here to control for different amounts of spacing
        self.date = re.sub("\s+", " ", self.content[0][1]).split(' ')[0]
        self.scan_process = self.content[0][4]
        self.well_plate_type = self.content[1][9]

        # This section assigns maps analytes to wells
        if self._has_scan_key():
            self.wells = self._assign_wells_from_scan_key()
        
        else:
            # Look in the well information table for anything
            for i, row in self.content.iterrows():
                if 'Well Info' in row[0]:
                    well_info_table_start = i + 1
                if 'End Annotation' in row[0]:
                    well_info_table_end = i
            
            # Debug well info table
            #print(well_info_table_start, well_info_table_end)
            #print(self.content.iloc[well_info_table_start + 1:well_info_table_end])

            info_table = self.content.iloc[well_info_table_start + 1:well_info_table_end].set_index(0).replace('MT', np.NaN).dropna(axis=0,how='all').dropna(axis=1,how='all')
            info_table.replace(np.NaN, None)

            # If the well info dataframe is empty, just assign the wells with no analyte information
            if info_table.empty:
                self.wells = [Well(scan, self.file) for scan in self.scan_list]
            else:
                # Gets the well information table as a dict of columns, where each column has rows (letters of well plate)
                d = {}
                for column, row_analyte_dict in info_table.to_dict().items():
                    row_letter, well_information = list(row_analyte_dict.keys())[0], list(row_analyte_dict.values())[0]
                    well = f"{row_letter}{column}"
                    d[well] = well_information
                self.wells = self._assign_wells_from_dict(d)

    @property
    def blocksize(self):
        '''
        Length of the well scans which is 1 for each wavelength plus the well label (A1, A2, H3, etc...)
        '''
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
        '''
        List of unformatted scan pd.DataFrame objects which can be interpreted by the EKKOScanFormats.Well class
        '''
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
        if well_label not in possible_wells:
            raise ValueError(f'{well_label} is not a valid well label.')

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
        potential_scan_keys = [
            Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scan_key.csv')),
            Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scan_key.xlsx')), 
            Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scankey.csv')), 
            Path(f'{self.file.parent}' / Path(f'{self.file.stem}' + '_scankey.xlsx'))
        ]

        for p in potential_scan_keys:
            if p.exists():
                self._scan_key = p
                return True
        
        return False   

    def _assign_wells_from_scan_key(self):
        '''Attempts to pull data about the scan file from a second file labeled experiment_summary_scan_key.csv. Can also be xlsx file'''

        if self._scan_key.suffix == '.csv':
            analyte_map = pd.read_csv(self._scan_key, header = None).set_index(0)[1].to_dict()
        elif self._scan_key.suffix == '.xlsx':
            analyte_map = pd.read_excel(self._scan_key, header = None).set_index(0)[1].to_dict()
        else:
            raise TypeError('Scan key file format not recognized')

        return self._assign_wells_from_dict(analyte_map)

    def _assign_wells_from_dict(self, d: dict):
        #print(f'PRocess: {self.scan_process}')
        #print(f'Length of scan list {len(self.scan_list)}')
        #print(f'Blocksize: {self.blocksize}')
        ##print(self.scandata)
        #print(f'Length of scan data: {len(self.scandata)}')
        #print(self.scan_list)
        #for s in self.scan_list:
        #    print(s)
        #    print('\n')
        local_wells = [Well(scan, self.file) for scan in self.scan_list]

        for well in local_wells:
            if well.name in d.keys():
                well.analyte = d[well.name]
        
        return local_wells



