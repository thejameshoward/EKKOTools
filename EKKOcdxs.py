import pandas as pd
import re
import numpy as np

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


class EKKOScanSummary():
    def __init__(self, file):
        self.file = file

        # Check to see if the file is a JASCO formatted csv
        if self.file[-5:] == ".cdxs" or ".CDXS":
            self.content = pd.read_csv((self.file), header=None, sep='\n')
            self.content = self.content[0].str.split('\t', expand=True)
            if self.content[0][0] != "Hinds Instruments CD Reader":
                raise ValueError(
                    "The file is not formatted like a EKKO CD Wellplate Reader cdxs file")
        else:
            raise ValueError("The file is not a cdxs file")

        self.wells = [_Well(scan) for scan in self.scan_list]
        self.name = self.content[0][2]
        self.date = self.content[0][1].split('   ')[0]
        self.date = self.content[0][1].split('   ')[1]

    @property
    def blocksize(self):
        digits = re.findall(r'\b\d+\b', self.content[0][4])
        block_size = (int(digits[1]) - int(digits[0])) / int(digits[2]) + 2
        return int(block_size)

    @property
    def scandata(self):
        df = pd.read_csv(self.file, skiprows=11, delimiter="\t",
                         error_bad_lines=False, usecols=["WL", "CD-mDeg", "ABS"])
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
        # These array positions are hard coded, so they may have to be changed
        first_column = self.content[0][12:]
        wells = []
        for row in first_column:
            if row in possible_wells:
                wells.append(row)
            else:
                pass
        return wells

    # Pass in a string containing the well name like "A1" or "H11" and get the CD of it
    def get_CD(self, well_name):
        for well in self.wells:
            if well.name == well_name:
                return well._get_CD()
        raise ValueError("Well {} not found".format(well_name))


class _Well():  # Well class, hand in a dataframe from scan_list and getout other stuff
    def __init__(self, df):
        self.df = df.reset_index()
        if not self.df["WL"][0] in possible_wells:
            raise ValueError("Well format not understood")
        else:
            self.name = self.df["WL"][0]
            self.df = self.df.drop(0)
            self.df = self.df.set_index("WL")

    def _get_CD(self):
        return {
            wl: self.df["CD-mDeg"][wl]
            for wl in self.df.index
        }
