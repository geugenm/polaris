"""
Module for fetching and decoding telemetry data
"""
import datetime
import json
import logging
import os
import subprocess
from collections import namedtuple

import pandas as pd
# import glouton dependencies
from glouton.domain.parameters.programCmd import ProgramCmd
from glouton.services.observation.observationsService import \
    ObservationsService

Satellite = namedtuple('Satellite', ['norad_id', 'name', 'decoder'])
SATELLITE_DATA_FILE = 'satellites.json'
SATELLITE_DATA_DIR = os.path.dirname(__file__)
_SATELLITES = json.loads(
    open(os.path.join(SATELLITE_DATA_DIR, SATELLITE_DATA_FILE)).read(),
    object_hook=lambda d: Satellite(d['norad_id'], d['name'], d['decoder']))

DATA_DIRECTORY = '/tmp/polaris'

LOGGER = logging.getLogger(__name__)


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


class NoSuchSatellite(Exception):
    """Raised when we can't identify the satellite requested
    """


class NoDecoderForSatellite(Exception):
    """Raised when we have no decoder
    """


def find_satellite(sat, satellites):
    """Find a match for a given satellite in a list of satellites
    """
    for candidate in satellites:
        if sat in (candidate.name, candidate.norad_id):
            print('Satellite: id={} name={} decoder={}'.format(
                candidate.norad_id, candidate.name, candidate.decoder))
            print('selected decoder={}'.format(candidate.decoder))
            if candidate.decoder is None:
                print('Satellite {} not supported!'.format(sat))
                raise NoDecoderForSatellite
            return candidate
    raise NoSuchSatellite


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

    try:
        satellite = find_satellite(sat, _SATELLITES)
    except Exception as exception:
        print("Can't find satellite or decoder: ", exception)
        raise exception

    decoder = satellite.decoder

    # Converting start date info into datetime object
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date).to_pydatetime()
    elif not isinstance(start_date, datetime.datetime):
        start_date = (datetime.datetime.utcnow() -
                      datetime.timedelta(seconds=3600))
    LOGGER.info("Fetch start date: %s", start_date)

    # Converting start date info into datetime object
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date).to_pydatetime()
    elif not isinstance(end_date, datetime.datetime):
        end_date = start_date + datetime.timedelta(seconds=3600)
    LOGGER.info("Fetch end date: %s", end_date)

    # Creating a new subdirectory to output directory
    # to collect glouton's data. Using start date to name it.
    cwd_path = os.path.join(
        output_directory,
        "data_" + str(start_date.timestamp()).replace('.', '_'))
    if not os.path.exists(cwd_path):
        os.mkdir(cwd_path)

    # Preparing glouton command configuration
    glouton_conf = ProgramCmd(norad_id=satellite.norad_id,
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
                              transmitter_type=None,
                              frame_modules=None,
                              observer=None,
                              app_source=None,
                              transmitter=None,
                              page_from=None,
                              page_to=None)

    # Running glouton data collection
    try:
        obs = ObservationsService(glouton_conf)
        obs.extract()
    except Exception as eee:  # pylint: disable=W0703
        LOGGER.error("data collection: %s", eee)
    LOGGER.info('Saving the dataframes in directory: %s', output_directory)
    LOGGER.info('Merging all the csv files into one CSV file.')
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
        LOGGER.info('Merge Completed')
        LOGGER.info('Storing merged CSV file: %s', merged_file)
    except subprocess.CalledProcessError as err:
        LOGGER.error(err)

    # Using satnogs-decoders to decode the CSV files containing
    # multiple dataframes and store them as JSON objects.
    LOGGER.info('Starting decoding of the data')
    decoded_file = os.path.join(output_directory, 'decoded_frames.json')
    decode_cmd = build_decode_cmd(merged_file, decoded_file, decoder)

    try:
        proc3 = subprocess.Popen(decode_cmd, shell=True, cwd=output_directory)
        proc3.wait()
        LOGGER.info('Decoding of data finished.')
    except subprocess.CalledProcessError as err:
        LOGGER.info('ERROR: %s', err)

    LOGGER.info('Stored the decoded data JSON file in root directory: %s',
                decoded_file)
