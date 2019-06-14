import subprocess
import os
import argparse


class Fetch(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data_fetch_decode()


def get_output_directory():
    all_directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    output_directory = max(all_directories, key=os.path.getmtime)
    return output_directory


def data_fetch_decode():
    start_date = '2019-05-01T00:00:00'
    end_date = '2019-05-10T00:00:00'
    data_directory = '../data'
    fetch_cmd = 'python3 ./glouton.py --wdir '+data_directory+' -s '+start_date+' -e '+end_date+' -n 43617 --demoddata --demodm CSV'
    try:
        subprocess.Popen(fetch_cmd, shell=True, cwd='../utils/glouton-satnogs-data-downloader')
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    output_directory = get_output_directory()
    print('Saving the dataframes in directory: '+output_directory)
    path_to_output_directory = data_directory+'/'+output_directory
    merge_cmd = 'sed 1d *.csv > ../merged_frames.csv'
    try:
        subprocess.Popen(merge_cmd, shell=True, cwd=path_to_output_directory)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    merged_file = 'merged_frames.csv'
    decode_cmd = 'python decode-multiple.py -d Elfin -p -x ../../data/'+merged_file+' > ../../data/decoded_frames.json'
    try:
        subprocess.Popen(decode_cmd, shell=True, cwd='../utils/satnogs-decoders/')
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
