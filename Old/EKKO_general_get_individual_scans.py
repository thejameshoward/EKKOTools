import os
import pandas as pd

'''
Program must be run in the top directory of an EKKO plate reader experiment. This folder will have a "Scans" subdirectory.
'''


def get_scanfiles():
    '''
    

    Returns
    -------
    list
        All .cdx files in the ./Scans/ directory. Returns Error 1 if no scans are found

    '''
    scan_list = []
    for file in os.listdir('./Scans/'):
        if file[-4:] == ".cdx" or file[-4:] == ".CDX":
            scan_list.append(file[:-4])
    if len(scan_list) == 0:
        print("No scans were found.")
        return 1
    return(scan_list)

def get_scandata(scan_list):
    '''
    Parameters
    ----------
    scan_list : list
        list of the files in the scan directory

    Returns
    -------
    Dictionary containing the well identifier (A1, B3, C9, etc...) as a key and a Pandas dataframe containing the scan information

    '''
    scan_data = {}
    for i in range(len(scan_list)):
        in_file = pd.read_csv('./Scans/{}.cdx'.format(scan_list[i]), skiprows=4, delim_whitespace=True)
        in_file.drop(['m', "CD-sample", "Xsample", "DCsample", 
                      "CD-base", "X-base", "DC-base", "PMT", "V", 
                      "DC-dark", "SENS"], axis=1, inplace=True)
        scan_data[scan_list[i]] = in_file
    return(scan_data)

def get_combined_output(scan_data, wavelengths):
    '''
        Parameters
    ----------
    scan_data, wavelengths : dictionary, list
        scan data from get_scandata() and wavelength list from get_wavelengths()

    Returns
    -------
    Pandas dataframe of all scan data with well identifiers as the first row
    '''
    master_data_list = pd.DataFrame(data=wavelengths, index=None, columns=None, dtype=None, copy=False)
    for scan in scan_data:
        data = scan_data[scan]
        
        #Add new row containing well name, resort index so it's at the top
        data.loc[-1] = [scan, scan, scan]
        data.index = data.index +1
        data = data.sort_index()
        
        #Remove wavelength column
        data.drop('WL', axis=1, inplace=True)
        master_data_list = pd.concat([master_data_list, data], axis=1)
    return master_data_list

def get_wavelengths(scan_data, scan_list):
    wavelengths = scan_data[scan_list[0]]["WL"] #Extracts wavelengths from first well plate reading. Assumes all wells measured same WL
    
    wavelengths.loc[-1] = ""
    wavelengths.index = wavelengths.index +1
    wavelengths = wavelengths.sort_index()
    return wavelengths


def get_cd(data, wavelengths):
    cd_only = pd.DataFrame(wavelengths)
    cd_only = cd_only.join(data["CD"])
    return cd_only

def get_abs(data, wavelengths):
    abs_only = pd.DataFrame(wavelengths)
    abs_only = abs_only.join(data["ABS"])
    return abs_only

def main():
    scan_list = get_scanfiles()
    scan_data = get_scandata(scan_list)
    wavelengths = get_wavelengths(scan_data, scan_list)
    
    data = get_combined_output(scan_data, wavelengths)
    
    cd_only = get_cd(data, wavelengths)
    abs_only = get_abs(data, wavelengths)
    
    data = cd_only.merge(abs_only, left_index=True, right_index=True, how='inner')
    
    data.to_csv('out.csv', index=False)
    
if __name__ == '__main__': 
    main()