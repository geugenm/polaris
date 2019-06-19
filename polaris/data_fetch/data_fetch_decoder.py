import subprocess
import os
import argparse


data_directory = '/tmp/polaris'


class Fetch(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data_fetch_decode()


def get_output_directory(data_directory=data_directory):
    """
    Utility function for getting the output directory.

    Currently it looks for the last-modified directory within
    the data_directory argument.
    """
    os.chdir(data_directory)
    all_directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    output_directory = max(all_directories, key=os.path.getmtime)
    return output_directory


def build_decode_cmd(src, dest):
    """Build command to decode downloaded into JSON
    """
    decode_multiple = 'python decode-multiple.py'
    decoder_module = 'Elfin'
    decode_cmd = '{decode_multiple} -d {decoder_module} -p -x {src} > ../../{dest}'.format(
        decode_multiple=decode_multiple,
        decoder_module=decoder_module,
        src=src,
        dest=dest,
    )
    return decode_cmd


def build_fetch_cmd():
    """Build command to fetch data from SatNOGS for a particular
    satellite
    """
    start_date = '2019-05-01T00:00:00'  # Start timestamp
    end_date = '2019-05-10T00:00:00'  # End timestamp
    glouton = 'python3 ./glouton.py'
    demod_args = '--demoddata --demodm CSV'
    sat = '43617'  # Elfin-B
    cmd = '{glouton} --wdir {data_dir} -s {start_date} -e {end_date} -n {sat} {demod_args}'.format(
        glouton=glouton,
        data_dir=data_directory,
        start_date=start_date,
        end_date=end_date,
        sat=sat,
        demod_args=demod_args
    )
    return cmd


def data_fetch_decode():
    """Main function to download and decode satellite telemetry"""
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    # Shell command for executing glouton in order to download the
    # dataframes from SatNOGS network based on NORAD ID of the
    # satellite and start and end timestamps
    fetch_cmd = build_fetch_cmd()
    try:
        # Using subprocess package to execute fetch command by passing
        # current working directory as an argument
        p1 = subprocess.Popen(fetch_cmd,
                              shell=True,
                              cwd='../utils/glouton-satnogs-data-downloader')
        p1.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    output_directory = get_output_directory()
    print('Saving the dataframes in directory: '+output_directory)
    path_to_output_directory = data_directory+'/'+output_directory
    print('Merging all the csv files into one CSV file.')
    merged_file = 'merged_frames_'+output_directory+'.csv'
    # Command to merge all the csv files from the output directory
    # into a single CSV file.
    merge_cmd = 'sed 1d *.csv > ../'+merged_file
    try:
        # Using subprocess package to execute merge command to merge CSV files.
        p2 = subprocess.Popen(merge_cmd,
                              shell=True,
                              cwd=path_to_output_directory)
        p2.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    print('Merge Completed')
    print('Storing merged CSV file: '+merged_file)
    print('Starting decoding of the data')
    decoded_file = 'decoded_frames_'+output_directory+'.json'
    # Using satnogs-decoders to decode the CSV files containing
    # multiple dataframes as a JSON objects.
    # decode-multiple.py is not present in satnogs-decoders repository
    # You can download the script from the code snippets [https://gitlab.com/librespacefoundation/satnogs/satnogs-decoders/snippets/1795023]
    # Put that script in polaris/utils/satnogs-decoders and you're good to go!
    decode_cmd = build_decode_cmd(merged_file, decoded_file)
    try:
        absolute_file_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(absolute_file_directory)
        # TODO: On the fence here about whether to use shell
        # direction to create the output file, or to capture output &
        # write to file ourselves.
        p3 = subprocess.Popen(decode_cmd,
                              shell=True,
                              cwd='../../utils/satnogs-decoders')
        p3.wait()
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    print('Decoding of data finished.')
    print('Storing the decoded data JSON file in root directory :'+decoded_file)
