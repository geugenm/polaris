"""
Module for fetching and decoding telemetry data
"""
import datetime
import os
import subprocess
from collections import namedtuple

import pandas as pd
# import glouton dependencies
from glouton.domain.parameters.programCmd import ProgramCmd
from glouton.services.observation.observationsService import \
    ObservationsService

Satellite = namedtuple('Satellite', ['norad_id', 'name', 'decoder'])

DATA_DIRECTORY = '/tmp/polaris'
_SATELLITES = [
    Satellite('41460', 'AAUSAT 4', 'Aausat4'),
    Satellite('99964', 'ACRUX-1', 'Acrux1'),
    Satellite('44352', 'ARMADILLO', 'Armadillo'),
    Satellite('40968', 'BISONSAT', 'Bisonsat'),
    Satellite('40014', 'BUGSAT-1', 'Bugsat1'),
    Satellite('42759', 'CAS-4B', 'Cas4'),
    Satellite('42761', 'CAS-4A', 'Cas4'),
    Satellite('43855', 'CHOMPTT', 'Chomptt'),
    Satellite('43666', 'CubeBel-1', 'Cubebel1'),
    Satellite('99999', 'CubeSatSim', 'Cubesatsim'),
    Satellite('43793', 'CSIM-FD', 'Csim'),
    Satellite('43616', 'ELFIN-B', 'Elfin'),
    Satellite('43617', 'ELFIN-A', 'Elfin'),
    Satellite('44431', 'EntrySat', 'Entrysat'),
    Satellite('43700', 'QO-100', 'Eshail2'),
    Satellite('43552', 'EQUiSat', 'Equisat'),
    Satellite('40967', 'FOX-1A', 'Fox'),
    Satellite('43017', 'FOX-1B', 'Fox'),
    Satellite('43770', 'FOX-1C', 'Fox'),
    Satellite('43137', 'FOX-1D', 'Fox'),
    Satellite('43468', 'IRAZU', 'Irazu'),
    Satellite('43693', 'IRVINE-01', 'Irvine'),
    Satellite('99915', 'IRVINE-02', 'Irvine'),
    Satellite('44420', 'LightSail-2', 'Lightsail2'),
    Satellite('41474', 'MINXSS', 'Minxss'),
    Satellite('43758', 'MinXSS 2', 'Minxss'),
    Satellite('44045', 'MySat-1', 'Mysat'),
    Satellite('43933', 'OrigamiSat-1', 'Origamisat1'),
    Satellite('43814', 'PW-Sat2', 'Pwsat2'),
    Satellite('42708', 'QBEE', 'Qbee'),
    Satellite('43595', 'SiriusSat-1', 'Siriussat'),
    Satellite('43596', 'SiriusSat-2', 'Siriussat'),
    Satellite('42789', 'SKCUBE', 'Skcube'),
    Satellite('39090', 'STRAND-1', 'Strand'),
    Satellite('40012', 'UNISAT-6', 'Us6'),
    Satellite('43880', 'UWE-4', 'Uwe4'),
]


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


def build_decode_cmd(src, dest, decoder):
    """ Build command to decode downloaded into JSON """
    decode_multiple = 'decode_multiple'
    decoder_module = decoder
    input_format = 'csv'
    decode_cmd = '{decode_multiple} --filename {src} --format {input_format}'\
                 ' {decoder_module} > {dest}'.format(
                     decode_multiple=decode_multiple,
                     decoder_module=decoder_module,
                     src=src,
                     input_format=input_format,
                     dest=dest,
                 )
    return decode_cmd  # pylint: disable=R0914


def data_fetch_decode(sat, output_directory, start_date, end_date):  # pylint: disable=R0914,R0915 # noqa: E501
    """
    Main function to download and decode satellite telemetry.

    :param sat: a NORAD ID or a satellite name.
    :param output_directory: only used parameter for now.
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    # Filter or transform input arguments
    demod_module = ["CSV"]

    decoder = None
    for satellite in _SATELLITES:
        if sat in (satellite.name, satellite.norad_id):
            print('INFO: Satellite: id={} name={} decoder={}'.format(
                satellite.norad_id, satellite.name, satellite.decoder))
            decoder = satellite.decoder
            sat = satellite.norad_id
            print('INFO: selected decoder={}'.format(decoder))
    if decoder is None:
        print('Error: Satellite {} not supported!'.format(sat))
        return

    # Converting start date info into datetime object
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date).to_pydatetime()
    elif not isinstance(start_date, datetime.datetime):
        start_date = (datetime.datetime.utcnow() -
                      datetime.timedelta(seconds=3600))
    print("INFO: Fetch start date: {}".format(start_date))

    # Converting start date info into datetime object
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date).to_pydatetime()
    elif not isinstance(end_date, datetime.datetime):
        end_date = start_date + datetime.timedelta(seconds=3600)
    print("INFO: Fetch end date: {}".format(end_date))

    # Creating a new subdirectory to output directory
    # to collect glouton's data. Using start date to name it.
    cwd_path = os.path.join(
        output_directory,
        "data_" + str(start_date.timestamp()).replace('.', '_'))
    if not os.path.exists(cwd_path):
        os.mkdir(cwd_path)

    # Preparing glouton command configuration
    glouton_conf = ProgramCmd(norad_id=sat,
                              ground_station_id=None,
                              start_date=start_date,
                              end_date=end_date,
                              observation_status=None,
                              working_dir=cwd_path,
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
    try:
        obs = ObservationsService(glouton_conf)
        obs.extract()
    except Exception as eee:  # pylint: disable=W0703
        print("ERROR, data collection: ", eee)
    print('Saving the dataframes in directory: ' + output_directory)
    print('Merging all the csv files into one CSV file.')
    merged_file = os.path.join(output_directory, 'merged_frames.csv')
    # Command to merge all the csv files from the output directory
    # into a single CSV file.
    merge_cmd = 'sed 1d ' \
                + os.path.join(cwd_path, 'demod*/*.csv') \
                + ' > ' + merged_file

    try:
        # Using subprocess package to execute merge command to merge CSV files.
        proc2 = subprocess.Popen(merge_cmd, shell=True, cwd=output_directory)
        proc2.wait()
        print('Merge Completed')
        print('Storing merged CSV file: ' + merged_file)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)

    # Using satnogs-decoders to decode the CSV files containing
    # multiple dataframes and store them as JSON objects.
    print('Starting decoding of the data')
    decoded_file = os.path.join(output_directory, 'decoded_frames.json')
    decode_cmd = build_decode_cmd(merged_file, decoded_file, decoder)

    try:
        proc3 = subprocess.Popen(decode_cmd, shell=True, cwd=output_directory)
        proc3.wait()
        print('Decoding of data finished.')
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)

    print('Stored the decoded data JSON file in root directory: ' +
          decoded_file)
