#!/usr/bin/env python3

import csv
import xlsxwriter
from sys import argv
import os
import glob

'''
A script to translate the data output file of the EKKO from going down to going sideways
'''

def main():
    # getting arguments for the script, newly ouputted csv and the path to the file of interest
    script, csv_name, path = argv

    # create workbook and sheet
    workbook = xlsxwriter.Workbook("{}.xlsx".format(csv_name))
    worksheet = workbook.add_worksheet()

    # concatenate files in script rather than using cat *
    concatenated_files = r"compiled.csv"
    out_file = csv.writer(open(concatenated_files, 'w'))

    # going through top directory and getting the file info from the averaged file
    for filename in glob.glob(os.path.join(path, '*.cdxs')):
        header_info = []
        in_file = csv.reader(open(filename, "r"), delimiter = " ")
        for row in in_file:
            line = []
            for entry in row:
                entry = entry.split('\t')
                line.append(entry)
            header_info.append(line)
        out_file.writerows(in_file)

    row = 0
    col = 0

    # writing out header info into a csv
    for line_info in header_info[:9]:
        for entry in line_info:
            for part in entry:
                worksheet.write_string(row, col, part)
                # worksheet.write_string(row, col, entry[0])
                col += 1
        row += 1
        col = 0

    found_annotation = False
    for line_info in header_info[:(len(header_info)-13)]:
        for entry in line_info:
            for part in entry:
                if (part == "Annotation:"):
                    found_annotation = True
                if (found_annotation == True):
                    worksheet.write_string(row, col, part)
                    col += 1
        if (found_annotation == True):
            row += 1
            col = 0


    

    # getting the actual data from individual files into a list!
    all_wells = []
    for filename in glob.glob(os.path.join(path+'/Scans', '*.cdx')):
        data_info = []
        in_file = csv.reader(open(filename, "r"), delimiter = " ")
        for row_entry in in_file:
            line = []
            for entry in row_entry:
                entry = entry.split('\t')
                line.append(entry)
            data_info.append(line)
        all_wells.append(data_info)
        out_file.writerows(in_file)

    # adding pertinent well info to a dictionary
    well_info = {}

    for cdxfile in all_wells:
        name = cdxfile[2][0][0].split('\\')
        name = name[len(name)-1]
        # making list to store wavelength, CD and ABS
        all_wavelengths = []
        for line in cdxfile[6:]:
            for wavelength in line:
                wavelength_data = []
                wavelength_data.append(float(wavelength[0]))
                wavelength_data.append(float(wavelength[2]))
                wavelength_data.append(float(wavelength[3]))
                wavelength_data.append(float(wavelength[9]))
                wavelength_data.append(float(wavelength[12]))
                all_wavelengths.append(wavelength_data)
        well_info[name] = all_wavelengths

    row += 1
    start_row = row
    last_file_name = "nuthin"

    for file, entry in (sorted(well_info.items())):
        last_file_name = file
        worksheet.write_string(row, col, "Wavelength")
        row += 1
        for x in range (4):
            for list_data in entry:
                worksheet.write_number(row, col, list_data[0])
                row += 1
            row += 1
        break
    col += 1

    temp_row = start_row

    for file, entry in (sorted(well_info.items())):
        if (file[0] != last_file_name[0]):
            col = 1
            row += 2
            start_row = row

        else:
            row = start_row

        worksheet.write_string(row, col, file)
        row += 1

        # print CD data
        for list_data in entry:
            worksheet.write_number(row, col, list_data[1])
            row += 1
        row += 1

        # print absorbance data
        for list_data in entry:
            worksheet.write_number(row, col, list_data[2])
            row += 1
        row += 1

        # print DC-Dark
        for list_data in entry:
            worksheet.write_number(row, col, list_data[3])
            row += 1
        row += 1

        # print SENS
        for list_data in entry:
            worksheet.write_number(row, col, list_data[4])
            row += 1
        row += 1

        col += 1
        last_file_name = file
        temp_row = row

main()