"""
Module for fetching and decoding telemetry data
"""
import datetime
import glob
import importlib
import json
import logging
import os
import re
import subprocess
import sys
from collections import namedtuple
from dateutil import parser

import pandas as pd
# import glouton dependencies
from glouton.domain.parameters.programCmd import ProgramCmd
from glouton.services.observation.observationsService import \
    ObservationsService
# from vinvelivaanilai.orbit import tle_fetch, predict_orbit
from vinvelivaanilai.storage import retrieve
from vinvelivaanilai.space_weather import sw_file_fetch, sw_extractor

from polaris.data.fetched_data_preprocessor import FetchedDataPreProcessor
from polaris.dataset.dataset import PolarisDataset

Satellite = namedtuple('Satellite',
                       ['norad_id', 'name', 'decoder', 'normalizer'])

SATELLITE_DATA_FILE = 'satellites.json'
SATELLITE_DATA_DIR = os.path.dirname(__file__)
_SATELLITES = json.loads(
    open(os.path.join(SATELLITE_DATA_DIR, SATELLITE_DATA_FILE)).read(),
    object_hook=lambda d: Satellite(d['norad_id'], d['name'], d['decoder'], d[
        'normalizer']))

NORMALIZER_LIB = 'contrib.normalizers.'

SUPPORTED_INDICES = ('DGD', 'DPD', 'DSD')

LOGGER = logging.getLogger(__name__)


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
    """Raised when we can't identify the satellite requested """


class NoDecoderForSatellite(Exception):
    """Raised when we have no decoder """


class NoNormalizerForSatellite(Exception):
    """Raised when we have no normalizer """


class NoCSVFilesToMerge(Exception):
    """Raised when there are no CSV files to merge or the downloaded
    CSV files have been modified"""


class NoDecodedFramesFile(Exception):
    """Raised when there is no file of decoded frames after attempting to
    download new frames.
    """


class SpecifiedImportFileDoesNotExist(Exception):
    """Raised when a specified file to be imported does not exist.
    """


def load_normalizer(sat):
    """
    Load the normalizer selected by name within the NORMALIZER_LIB.

    :param sat: a satellite object.

    :returns: the loaded normalizer.
    """
    if sat.normalizer is None:
        raise NoNormalizerForSatellite
    try:
        loaded_normalizer = importlib.import_module(NORMALIZER_LIB +
                                                    sat.normalizer.lower())
        normalizer = getattr(loaded_normalizer, sat.normalizer)
        return normalizer
    except Exception as eee:
        LOGGER.error("Normalizer loading: %s", eee)
        raise eee


def find_satellite(sat, sat_list):
    """Find a match for a given satellite in a list of satellites """
    for candidate in sat_list:
        if sat in (candidate.name, candidate.norad_id):
            LOGGER.info('Satellite: id=%s name=%s decoder=%s',
                        candidate.norad_id, candidate.name, candidate.decoder)
            LOGGER.info('selected decoder=%s', candidate.decoder)
            if candidate.decoder is None:
                LOGGER.error('Satellite %s not supported!', sat)
                raise NoDecoderForSatellite
            return candidate
    raise NoSuchSatellite


def build_start_and_end_dates(start_date, end_date):
    """
    Build start and end dates using either provided string, provided
    datetime object, or choosing default.

    Default period starts one hour before UTC current time at call.

    """
    # First start date; if no date provided, set to an hour ago.
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    elif not isinstance(start_date, datetime.datetime):
        start_date = (pd.Timestamp.utcnow() - pd.to_timedelta(3600, unit="s"))

    # Next end date; if no end date provided, set to an hour after start_date
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    elif not isinstance(end_date, datetime.datetime):
        end_date = start_date + pd.to_timedelta(3600, unit="s")

    return start_date, end_date


def merge_csv_files(output_directory, path):
    """
    Merge all the CSV files inside path into a single file.

    :returns: path of the merged file.
    """
    LOGGER.info('Merging all the csv files into one CSV file.')
    merged_file = os.path.join(output_directory, 'merged_frames.csv')
    for filename in glob.glob(os.path.join(path, 'demod*/*.csv')):
        with open(filename, 'r') as source:
            content = source.read()
            with open(merged_file + '.tmp', 'a') as target:
                target.write(content)

    if os.path.exists(merged_file + '.tmp'):
        pass
    else:
        LOGGER.warning(' '.join([
            'There are no CSV files to merge.  This can happen',
            'if the time range specified had no frames to download,'
            'or if the downloaded files were deleted or modified',
            'during exeution.'
        ]))
        raise NoCSVFilesToMerge

    with open(merged_file + '.tmp', 'r') as source:
        with open(merged_file, 'w') as target:
            for line in sorted(source):
                target.write(line)
    os.remove(merged_file + '.tmp')
    LOGGER.info('Merge Completed')

    return merged_file


def data_fetch(norad_id, output_directory, start_date, end_date):
    """
    Fetch data of the sat with the given Norad ID gathered between start_date
    and end_date. Data is retrieved from SatNOGS database using Glouton.

    :returns: path of the file that contains the fetched data.
    """

    # Creating a new subdirectory to output directory
    # to collect glouton's data. Using start date to name it.
    cwd_path = os.path.join(output_directory,
                            "data_" + start_date.strftime("%Y-%m-%d_%H-%M-%S"))
    if not os.path.exists(cwd_path):
        os.mkdir(cwd_path)

    # Preparing glouton command configuration
    glouton_conf = ProgramCmd(norad_id=norad_id,
                              ground_station_id=None,
                              start_date=start_date,
                              end_date=end_date,
                              observation_status=None,
                              working_dir=cwd_path,
                              archives=False,
                              waterfalls=False,
                              demoddata=True,
                              archive_modules=None,
                              demoddata_modules=["CSV"],
                              waterfall_modules=None,
                              user=None,
                              transmitter_uuid=None,
                              transmitter_mode=None,
                              transmitter_type=None,
                              frame_modules=None,
                              observer=None,
                              app_source=None,
                              transmitter=None)

    # Running glouton data collection
    try:
        obs = ObservationsService(glouton_conf)
        obs.extract()
    except Exception as eee:  # pylint: disable=W0703
        LOGGER.error("data collection: %s", eee)

    LOGGER.info('Saving the dataframes in directory: %s', output_directory)
    try:
        return merge_csv_files(output_directory, cwd_path)
    except NoCSVFilesToMerge:
        return ""


def build_decoded_file_path(directory):
    """Return path to decoded files within directory

    :param directory: full path to directory for decoded frames

    :returns: path of the file that contains the decoded data.
    """
    return os.path.join(directory, 'decoded_frames.json')


def data_merge_and_decode(decoder, output_directory, new_frames_file=""):
    """
    Decode the data found in frames_file using the given decoder. Put it in
    output_directory.

    :returns: path of the file that contains the decoded data.
    """

    # Using satnogs-decoders to decode the CSV files containing
    # multiple dataframes and store them as JSON objects.

    decoded_file = build_decoded_file_path(output_directory)

    if new_frames_file == "":
        LOGGER.info('No new frames to decode and merge')
    else:
        LOGGER.info('Starting decoding and merging of the new frames')
        decode_cmd = build_decode_cmd(new_frames_file, decoded_file, decoder)
        try:
            proc3 = subprocess.Popen(decode_cmd,
                                     shell=True,
                                     cwd=output_directory)
            proc3.wait()
            LOGGER.info('Decoding of data finished.')
        except subprocess.CalledProcessError as err:
            LOGGER.error('Error running %s: %s', decode_cmd, err)

    if os.path.exists(decoded_file):
        LOGGER.info('Decoded data stored at %s', decoded_file)
        return decoded_file

    LOGGER.error(' '.join([
        'There is no file of decoded frames at ' + decoded_file,
        'This can happen if the time range specified had no frames'
        'to download, and you have not imported frames already.'
        'You may want to specify a different time range'
        'with the --start_date and --end_date options, or import'
        'frames downloaded directly from SatNOGS.  This',
        'can also arise if the downloaded files have been',
        'deleted or modified during execution.'
    ]))
    raise NoDecodedFramesFile


def load_frames_from_json_file(file):
    """Load frames from a JSON file.

    :param file: a JSON file
    :returns: a list of frames
    """
    with open(file) as f_handle:
        try:
            # pylint: disable=W0108
            decoded_frame_list = json.load(f_handle)
        except json.JSONDecodeError:
            LOGGER.error("Cannot load % - is it a valid JSON document?", file)
            raise json.JSONDecodeError

    return decoded_frame_list


def get_times_from_frames_list(list_of_frames, key='time'):
    """Gets the time list from decoded_frames list

    :param list_of_frames: List containing the decoded frames
    :type list_of_frames: list
    :param key: Name of the time key in the dictionares, defaults to 'time'
    :type key: str, optional
    :return: List of timestamps taken from list_of_frames
    :rtype: list
    """
    return [frame[key] for frame in list_of_frames]


def write_or_merge(dataset, file, strategy):
    """Write dataset to output_file; if output file already exists, follow
    strategy: overwrite, merge or error.

    """
    def write_dataset(dataset, file):
        with open(file, 'w') as f_handle:
            f_handle.write(dataset.to_json())

    file_exists = os.path.exists(file)

    if strategy == 'overwrite':
        LOGGER.info('Overwriting existing file')
        write_dataset(dataset, file)
    elif strategy == 'error' and file_exists is True:
        raise FileExistsError(
            'Output file already exists, refusing to overwrite.')
    else:
        # Default strategy is merge.

        # Take copy of dataset, so that we don't change the original
        # object.
        dataset_for_writing = PolarisDataset(metadata=dataset.metadata,
                                             frames=dataset.frames)
        if file_exists is True:
            try:
                LOGGER.debug('Trying to load dataset from %s', file)
                existing_dataset = load_frames_from_json_file(file)
                dataset_for_writing.frames = existing_dataset[
                    'frames'] + dataset.frames
            except json.JSONDecodeError:
                LOGGER.info("File exists but cannot parse it")
        write_dataset(dataset_for_writing, file)


def data_normalize(normalizer, frame_list):
    """
    Normalize the data found in frame_list using the given normalizer.

    :returns: list of normalized frames
    """
    # Normalize values
    normalized_frames = []
    frame_count = 0
    for frame in frame_list:
        frame_count += 1
        frame_norm = normalizer.normalize(frame)
        if not normalizer.validate_frame(frame_norm):
            LOGGER.debug("Skipping frame %d because validation failed",
                         frame_count)
            continue
        normalized_frames.append(frame_norm)
    return normalized_frames


def normalize_satname(sat_name):
    """
    Normalize satellite name for comparison or searching

    :param sat_name: Satellite name
    """
    return re.sub('[^A-Za-z0-9]+', '', sat_name).lower()


def find_alternatives(sat_name, list_of_satellites):
    """
    Find an alternative for sat_name from dict_of_satellites

    :param sat_name: Name of satellite to check
    :param list_of_satellites: Dictionary containing
           all satellite details
    """
    for sat_present in list_of_satellites:
        if normalize_satname(sat_name) == normalize_satname(sat_present.name):
            return sat_present.name

    return None


def filter_data(start_date, end_date, data):
    """
    Filters data based on date

    :param start_date: Initial date for filtering
    :type start_date: datetime.datetime
    :param end_date: Final date for filtering
    :type end_date: datetime.datetime
    :param data: Data to filter
    :type data: pd.DataFrame
    :raises ValueError: If data.index is not pd.DatetimeIndex
    :return: Filtered data with index between start_date and end_date
    :rtype: pd.DataFrame
    """
    if data.index is not pd.DatetimeIndex:
        raise ValueError("Expected {} for index".format(pd.DatetimeIndex))

    f_data = data[(data.index > start_date) & (data.index <= end_date)]

    return f_data


def fetch_sw(start_date, end_date, cache_dir, indices=SUPPORTED_INDICES):
    """
    Fetch Space Weather indices using vinvelivaanilai.

    :param start_date: Start date of space weather data to fetch
    :type start_date: datetime.datetime
    :param end_date: End date of space weather data to fetch
    :type end_date: datetime.datetime
    :param cache_dir: Cache directory where downloaded files are stored
    :type cache_dir: str
    :param indices: List of indices to fetch, defaults to SUPPORTED_INDICES
    :type indices: list, optional
    :return: Dictionary of dataframes containing indices fetched
    :rtype: dict of pd.DataFrame
    """
    data = {}
    for index in indices:
        print(start_date, end_date)
        logging.getLogger().setLevel(logging.DEBUG)
        data[index] = sw_file_fetch.fetch_indices(index, start_date, end_date,
                                                  cache_dir)

    return data


def fetch_or_import_sw(start_date, end_date, cache_dir, **kwargs):
    """
    Fetch/import space weather from vinvelivaanilai/txt/influxdb.

    :param start_date: Start date of data to fetch
    :type start_date: str
    :param end_date: End date of data to fetch
    :type end_date: str
    :param cache_dir: Path to cache directory
    :type cache_dir: str

    :return: Dictionary with index as space_weather indices and values as
        corresponding pd.DataFrame
    :rtype: dict of pd.DataFrame
    """
    # Get the times as datetime objects
    local_start_date = parser.parse(start_date)
    local_end_date = parser.parse(end_date)

    # Download the data
    data = fetch_sw(local_start_date, local_end_date, cache_dir)

    for index in data:
        # vv fetches data per year/quarter. This reduces the data to that
        # between start and end dates
        data[index] = filter_data(local_start_date, local_end_date,
                                  data[index])

    return data


def fetch_nearest_sw(sw_data, time_list):

    time_df = pd.to_datetime(time_list)
    processed_data = {}
    for index in sw_data:
        processed_data[index] = retrieve.get_multiple_nearest_from_df(
            time_df, sw_data[index])

    return processed_data


def fetch_or_import(import_file, satellite, start_date, end_date, cache_dir):
    """
    Its a import_file validation function,
    it checks if variable import_file variable is empty or not,
    if its not empty then it checks if the file exists or not,
    if the file does not exit, it will raise an error.

    :param import_file: file to be checked if exists or not
    :param satellite: satellite whose data is to be fetch
    :param start_date: start date of data to fetch
    :param end_date: end date of data to fetch
    :param cache_dir: where temp output data should go
    returns: file if exists
    """
    # Retrieve, decode and normalize frames
    if import_file is None:
        # Converting dates into datetime objects
        start_date, end_date = build_start_and_end_dates(start_date, end_date)
        LOGGER.info('Fetch period: %s to %s', start_date, end_date)

        new_frames_file = data_fetch(satellite.norad_id, cache_dir, start_date,
                                     end_date)
    else:
        # If file is specified, retrieve from file
        if not os.path.isfile(import_file):
            raise SpecifiedImportFileDoesNotExist(
                'Import file does not exist.')
        new_frames_file = import_file
    return new_frames_file


def files_in_current_dir():
    """
    returns: list of csv and json files in the current directory.
    """
    candidate_files = [
        f for f in os.listdir()
        if os.path.isfile(f) and (f[-3:] == 'csv' or f[-4:] == 'json')
    ]
    return candidate_files


# pylint: disable-msg=too-many-arguments
# pylint: disable-msg=too-many-locals
def data_fetch_decode_normalize(sat, start_date, end_date, output_file,
                                cache_dir, import_file,
                                existing_output_file_strategy):
    """
    Main function to download and decode satellite telemetry.

    :param sat: a NORAD ID or a satellite name.
    :param start_date: start date of data to fetch
    :param end_date: end date of data to fetch
    :param output_file: where output should go
    :param cache_dir: where temp output data should go
    :param import_file: file containing data frames to import
    :param existing_output_file_strategy: what to do with existing
           output files: merge, overwrite or error.
    """
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Check if satellite info available
    try:
        satellite = find_satellite(sat, _SATELLITES)
    except Exception as exception:
        LOGGER.error("Can't find satellite or decoder: %s", exception)
        LOGGER.info("You can check for your satellite 'name' in %s",
                    str(os.path.join(SATELLITE_DATA_DIR, SATELLITE_DATA_FILE)))
        # Check if there is a satellite with a similar name
        alt_sat = find_alternatives(sat, _SATELLITES)
        if alt_sat is not None:
            LOGGER.info("Did you mean: %s?", alt_sat)
        raise exception

    # Try fetching data (from glouton/file)
    try:
        new_frames_file = fetch_or_import(import_file, satellite, start_date,
                                          end_date, cache_dir)
    except SpecifiedImportFileDoesNotExist:
        LOGGER.critical(' '.join([
            'Import file does not exist.', 'Some Suggestions:- ',
            ' '.join(files_in_current_dir())
        ]))
        sys.exit(1)

    decoded_frames_file = data_merge_and_decode(satellite.decoder, cache_dir,
                                                new_frames_file)
    decoded_frame_list = load_frames_from_json_file(decoded_frames_file)
    sw_data = fetch_or_import_sw(start_date, end_date, cache_dir)
    time_list = get_times_from_frames_list(decoded_frame_list)

    pro_sw_data = fetch_nearest_sw(sw_data, time_list)

    print(pro_sw_data)

    try:
        normalizer = load_normalizer(satellite)
    except Exception as exception:
        LOGGER.error("Can't load satellite normalizer: %s", exception)
        raise exception

    LOGGER.info('Loaded normalizer=%s', satellite.normalizer)
    normalized_frames = data_normalize(normalizer(), decoded_frame_list)
    polaris_dataset = PolarisDataset(metadata={
        "satellite_norad": satellite.norad_id,
        "satellite_name": satellite.name,
        "total_frames": len(normalized_frames)
    },
                                     frames=normalized_frames)

    LOGGER.info('Tagging columns')
    tagger = FetchedDataPreProcessor()
    tags = tagger.tag_columns(polaris_dataset)
    polaris_dataset.metadata["analysis"] = tags
    LOGGER.info('Tagging Completed')

    try:
        write_or_merge(polaris_dataset, output_file,
                       existing_output_file_strategy)
        LOGGER.info('Output file %s', output_file)
    except FileExistsError:
        LOGGER.critical(' '.join([
            'Output file exists and told not to overwrite it.',
            'Remove it, or try a different argument',
            'for --existing-output-file-strategy.'
        ]))
        sys.exit(1)
