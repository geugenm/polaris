import subprocess
import os
import argparse


class Fetch(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data_fetch_decode()


# Utility function for getting last modified directory.


def get_output_directory():
    data_directory_name = '/tmp/polaris/'
    if not os.path.exists(data_directory_name):
        os.makedirs(data_directory_name)
    os.chdir(data_directory_name)
    all_directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    output_directory = max(all_directories, key=os.path.getmtime)
    return output_directory


def data_fetch_decode():
    start_date = '2019-05-01T00:00:00'  # Start timestamp
    end_date = '2019-05-10T00:00:00'  # End timestamp
    data_directory = '/tmp/polaris'
    # Shell command for executing glouton in order to download the dataframes from SatNOGS network based on NORAD ID of the satellite and start and end timestamps
    fetch_cmd = 'python3 ./glouton.py --wdir '+data_directory+' -s '+start_date+' -e '+end_date+' -n 43617 --demoddata --demodm CSV'
    try:
        # Using subprocess package to execute fetch command by passing current working directory as an argument
        p1 = subprocess.Popen(fetch_cmd, shell=True, cwd='../utils/glouton-satnogs-data-downloader')
        p1.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    output_directory = get_output_directory()
    print('Saving the dataframes in directory: '+output_directory)
    path_to_output_directory = data_directory+'/'+output_directory
    print('Merging all the csv files into one CSV file.')
    merged_file = 'merged_frames_'+output_directory+'.csv'
    # Command to merge all the csv files from the output directory into a single CSV file.
    merge_cmd = 'sed 1d *.csv > ../'+merged_file
    try:
        # Using subprocess package to execute merge command to merge CSV files.
        p2 = subprocess.Popen(merge_cmd, shell=True, cwd=path_to_output_directory)
        p2.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    print('Merge Completed')
    print('Storing merged CSV file: '+merged_file)
    print('Starting decoding of the data')
    decoded_file = 'decoded_frames_'+output_directory+'.json'
    # Using satnogs-decoders to decode the CSV files containing multiple dataframes as a JSON objects.
    # decode-multiple.py is not present in satnogs-decoders repository
    # You can download the script from the code snippets [https://gitlab.com/librespacefoundation/satnogs/satnogs-decoders/snippets/1795023]
    # Put that script in polaris/utils/satnogs-decoders and you're good to go!
    decode_cmd = 'python decode-multiple.py -d Elfin -p -x /tmp/polaris/'+merged_file+' > ../../'+decoded_file
    try:
        absolute_file_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(absolute_file_directory)
        p3 = subprocess.Popen(decode_cmd, shell=True, cwd='../../utils/satnogs-decoders')
        p3.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    print('Decoding of data finished.')
    print('Storing the decoded data JSON file in root directory :'+decoded_file)
