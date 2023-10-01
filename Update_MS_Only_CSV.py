import os
import os.path
import re
import csv
import pandas as pd
import sys
import calendar



def main():

    # Sets base directory for searching for information

    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):

        base_dir = (sys.argv[1])

    if len(sys.argv) >> 2:
        print("Only one command argument allowed (path to search directory)")

    else:

        ###CHANGE THIS WHEN MOVING TO NEW SYSTEM (If you didn't using a command line)

        base_dir = ('F:\\')

    # Find xml files and store in list

    path_to_extern = find_ms_files(base_dir)
    big_list = []

    #Extracts all usefull information

    for i in range(len(path_to_extern)):

        try:

            extern_info = (extern_extract(path_to_extern[i]))
            header_info = header_extract(extern_path_to_header(path_to_extern[i]))
            path = [path_to_extern[i]]
            filename = [os.path.basename((os.path.dirname(path_to_extern[i])))]


            # Stores info in a list of lists

            big_list.append(filename + extern_info + header_info + path)

        except:
            print("Error at" + str(path_to_extern[i]))

    # Converts to a dataframe

    master_df = pd.DataFrame(big_list)

    column_names = [

            "Filename"              ,
            "Cone Voltage"          ,
            "Capillary Voltage"     ,
            "Quad Set Mass"         ,
            "Trap Voltage"          ,
            "Transfer Voltage"      ,
            "TW_height (V)"         ,
            "TW_velocity (m/s)"     ,
            "Post Trap Bias (V)"    ,
            "Post Trap Gradient (V)",
            "Desolvation Temp (C)"  ,
            "Desolvation Flow Rate" ,
            "Attenuation ON/OFF"    ,
            "Attenuation %"         ,
            "Quad ON/OFF"           ,
            "W/V Mode"              ,
            "Date Collected"        ,
            "Time (hour.min)"       ,
            "File Location"         ,
            ]

    master_df.columns = column_names


    # Save dataframe as CSV file in current working directory
    cwd = os.getcwd()
    path = cwd + "/MS_only_CSV" + ".csv"
    master_df.to_csv(path)



# Function to find xml files with logic to ensure they are correct

def find_xml_files(directory):
    path_to_xml = []
    for root, dirs, files in os.walk(directory):
        # exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('$')]
        if '_extern.inf' in files:
            dir_name = os.path.basename(root)
            for file in files:
                if file.endswith('.xml') and file == dir_name.replace('.raw', '.xml'):
                    path_to_xml.append(os.path.join(root, file))
    return path_to_xml

# Function to find ms only data with logic to ensure they are correct

def find_ms_files(directory):
    path_to_xml = []
    path_to_MS = []
    for root, dirs, files in os.walk(directory):
        # exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('$')]
        if '_extern.inf' in files:
            dir_name = os.path.basename(root)
            for file in files:
                if dir_name.endswith('dt.raw'):
                    pass
                elif file.endswith('.xml') and file == dir_name.replace('.raw', '.xml'):
                    path_to_xml.append(os.path.join(root, file))
                elif len(files) <=9 and file.endswith('extern.inf'):
                    path_to_MS.append(os.path.join(root, '_extern.inf'))
    return path_to_MS



# Functions that takes a path to an extern file as input and outputs the path to the header file


def extern_path_to_header(path):
	return path.replace('_extern.inf', '_header.txt')


# Dictionary that defines which lines of the extern (as CSV) contain valuable information

extern_dict = {

        "Cone Voltage"          : 234,
        "Capillary Voltage"     : 208,
        "Quad Set Mass"         : 8,
        "Trap Voltage"          : -2,
        "Transfer Voltage"      : -1,
        "TW_height (V)"         : 78,
        "TW_velocity (m/s)"     : 81,
        "Post Trap Bias (V)"    : 128,
        "Post Trap Gradient (V)": 127,
        "Desolvation Temp (C)"  : 214,
        "Desolvation Flow Rate" : 213

}

# Initialize dataframe to store all values
#master_df = pd.DataFrame(xml_filenames)


# Function that uses the extern conversion dictionary to extract the relevant information from the extern as a dataframe
def extern_extract(extern_path):

    l = []

    extern_df = (pd.read_csv(extern_path, sep = "\\t", engine='python'))


    for setting in (extern_dict):
        l.append((extern_df).iloc[extern_dict[setting]][0])

    # Only write attenuation setting if attenuation is on

    atten_dict = {
        0 : "OFF",
        1 : "ON"
    }

    if (atten_dict[(float(extern_df.iloc[104][0]))]) != 'OFF':
        l.append("ON")
        l.append(extern_df.iloc[111][0])
    else:
        l.append("OFF")
        l.append('N/A')


    # Check to see if quad is on or off

    if extern_df.iloc[-19][0] != "MSMS":
        l.append('OFF')
        l.append(extern_df.iloc[-17][0])
    else:
        l.append('ON')
        l.append(extern_df.iloc[-18][0])

    return l


 # Pull date and time from header

def header_extract(header_path):

    l = []

    header_df = pd.read_csv(header_path, sep = "\\t", engine='python')

    date = ((header_df.iloc[0][0])[18:])
    time = ((header_df.iloc[1][0])[18:])

    month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    abbrev_list = calendar.month_name[1:13]

    for i in range(len(abbrev_list)):

        abbrev_list[i] = abbrev_list[i][0:3]

    month_dict = dict(zip(abbrev_list, month_list))

    day = date[0:2]
    mon = month_dict[date[3:6]]
    year = date[7:11]

    new_date = (year + "-" + mon + "-" + day)

    new_time = (time[0:2] + "." + time[3:5])

    l.append(new_date)
    l.append(new_time)

    return l



# Extracts all pertinant XML information as a list of lists

def xml_extract(path_to_xml):

    if os.path.exists(path_to_xml):


        # Create a dictionary that converts cyclic seuence numbers to their respective functions

        sequence_numbers = ['0', '1', '6', '10', '12', '14']
        sequence_list = ['Inject', 'Separate', 'Eject and acquire', 'Eject to pre-store', 'Reinject from pre-store', 'Eject']
        sequence_dict = {sequence_numbers[i]: sequence_list[i] for i in range(len(sequence_numbers))}

        # List to store XML data
        xml_list = []

        # Open xml file

        with open(path_to_xml) as f:
            xml_file = f.read()



            # Find relevant information
            function = re.findall('"CyclicFunction" Value="(.*)"', xml_file)
            times = re.findall('"Time" Value="(.*)"', xml_file)
            times.append('13.20')
            pre_array_grad = re.findall('PreArrayGradient" Value="(.*)"', xml_file)
            pre_array_bias = re.findall('PreArrayBias" Value="(.*)"', xml_file)
            ej_volt = re.findall('WaveAmp" Value="(.*)"', xml_file)

            # Count the number of cyclic sequence steps
            numsteps = xml_file.count('CyclicFunction')

            seq_list = []

            for i in range(numsteps):

                seq_list.append(sequence_dict[function[i]])

                xml_list.append(seq_list)
                xml_list.append(times)
                xml_list.append(pre_array_grad)
                xml_list.append(pre_array_bias)


        return xml_list


# Only retrieves ejection height from XML
def xml_ej_height(path_to_xml):

    with open(path_to_xml) as f:
        xml_file = f.read()

        ej_volt = re.findall('WaveAmp" Value="(.*)"', xml_file)[-1]

    return ej_volt



if __name__ == "__main__":
    main()





