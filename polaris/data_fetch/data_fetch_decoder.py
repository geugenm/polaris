import os
import subprocess
import datetime

import pandas as pd

# import glouton
from glouton.domain.parameters.programCmd import ProgramCmd
from glouton.services.observation.observationsService import ObservationsService

DATA_DIRECTORY = '/tmp/polaris'


def get_output_directory(data_directory=DATA_DIRECTORY):
    """
    Utility function for getting the output directory.

    Currently it looks for the last-modified directory within
    the DATA_DIRECTORY argument.
    """
    os.chdir(data_directory)
    all_directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    output_directory = max(all_directories, key=os.path.getmtime)
    return output_directory


def build_truncate_first_line_cmd(src):
    """ Build command to truncate the first line from the output JSON file
    which is 'Input file' line resulting from decode_multiple script
    from satnogs-decoders.
    """
    truncate_cmd = 'sed -i {src} -e \'1d;\''.format(
        src=src,
        )
    return truncate_cmd


def build_decode_cmd(src, dest):
    """Build command to decode downloaded into JSON
    """
    decode_multiple = 'decode_multiple'
    decoder_module = 'Elfin'
    input_format = 'csv'
    decode_cmd = '{decode_multiple} --filename {src} --format {input_format}'\
        ' {decoder_module} > {dest}'.format(
                                    decode_multiple=decode_multiple,
                                    decoder_module=decoder_module,
                                    src=src,
                                    input_format=input_format,
                                    dest=dest,
                                    )
    return decode_cmd


def build_fetch_cmd():
    """Build command to fetch data from SatNOGS for a particular
    satellite
    """
    start_date = '2019-05-05T00:00:00'  # Start timestamp
    end_date = '2019-05-10T00:00:00'  # End timestamp
    glouton = 'python3 ./glouton.py'
    demod_args = '--demoddata --demodm CSV'
    sat = '43617'  # Elfin-A
    cmd = '{glouton} --wdir {data_dir} -s {start_date} -e {end_date} -n'\
        ' {sat} {demod_args}'.format(
                    glouton=glouton,
                    data_dir=DATA_DIRECTORY,
                    start_date=start_date,
                    end_date=end_date,
                    sat=sat,
                    demod_args=demod_args
                    )
    return cmd


def data_fetch_decode(sat_name, output_directory, start_date, end_date):
    """Main function to download and decode satellite telemetry

    :param sat_name: must be a NORAD ID, else TODO transform it into norad id.
    :param output_directory: only used parameter for now.
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    # Filter or transform input arguments
    demod_module = ["CSV"]

    # TODO transform sat_name into norad id if not a norad id
    sat_name = '43617'  # Elfin-A

    # Converting start date info into datetime object
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date).to_pydatetime()
    elif not isinstance(start_date, datetime.datetime):
        start_date = (datetime.datetime.utcnow()
                      - datetime.timedelta(seconds=3600))

    # Converting start date info into datetime object
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date).to_pydatetime()
    elif not isinstance(end_date, datetime.datetime):
        end_date = start_date + datetime.timedelta(seconds=3600)

    # TODO create a new subdirectory to output directory
    # to collect glouton's data

    # Preparing glouton command configuration
    # glouton_conf = glouton.domain.parameters.programCmd.ProgramCmd(
    glouton_conf = ProgramCmd(
            norad_id=sat_name,
            ground_station_id=None,
            start_date=start_date,
            end_date=end_date,
            observation_status=None,
            working_dir=output_directory,
            payloads=False,
            waterfalls=False,
            demoddata=True,
            payload_modules=None,
            demoddata_modules=demod_module,
            waterfall_modules=None,
            user=None,
            transmitter_uuid=None,
            transmitter_mode=None,
            transmitter_type=None)

    # Running glouton data collection
    # try:
        # obs = glouton.services.observation.observationsService \
        #      .ObservationsService(glouton_conf)
    obs = ObservationsService(glouton_conf)
    obs.extract()
    # except Exception as eee:
    #     print("ERROR, data collection: ", eee)

    #  # Shell command for executing glouton in order to download the
    #  # dataframes from SatNOGS network based on NORAD ID of the
    #  # satellite and start and end timestamps
    #  fetch_cmd = build_fetch_cmd()

    #  try:
    #      # Using subprocess package to execute fetch command by passing
    #      # current working directory as an argument
    #      p1 = subprocess.Popen(fetch_cmd,
    #                            shell=True,
    #                            cwd='../utils/glouton-satnogs-data-downloader')
    #      p1.wait()
    #  except subprocess.CalledProcessError as err:
    #      print('ERROR:', err)

    # not used anymore:
    # output_directory = get_output_directory()
    print('Saving the dataframes in directory: '+output_directory)
    # path_to_output_directory = DATA_DIRECTORY+'/'+output_directory
    print('Merging all the csv files into one CSV file.')
    merged_file = os.path.join(output_directory, 'merged_frames.csv')
    print("DEBUG    "+merged_file)
    # Command to merge all the csv files from the output directory
    # into a single CSV file.
    merge_cmd = 'sed 1d ' \
                + os.path.join(output_directory, '*.csv') \
                + ' > ' + merged_file
    print("DEBUG   "+merge_cmd)

    try:
        # Using subprocess package to execute merge command to merge CSV files.
        p2 = subprocess.Popen(merge_cmd,
                              shell=True,
                              cwd=output_directory)
        p2.wait()
        print('Merge Completed')
        print('Storing merged CSV file: '+merged_file)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)

    print('Starting decoding of the data')
    decoded_file = os.path.join(output_directory, 'decoded_frames.csv')
    # Using satnogs-decoders to decode the CSV files containing
    # multiple dataframes and store them as JSON objects.
    decode_cmd = build_decode_cmd(merged_file, decoded_file)

    try:
        absolute_file_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(absolute_file_directory)
        p3 = subprocess.Popen(decode_cmd,
                              shell=True,
                              cwd='../../utils/satnogs-decoders')
        p3.wait()
        print('Decoding of data finished.')
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
    truncate_cmd = build_truncate_first_line_cmd(decoded_file)
    try:
        p4 = subprocess.Popen(truncate_cmd,
                              shell=True,
                              cwd='../../')
        p4.wait()
        print(
            'Storing the decoded data JSON file in root directory :'
            + decoded_file
        )
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
