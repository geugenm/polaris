"""
Helpers to incorporate data from different sources.

General input standard format for functions in polaris learn are Pandas
Dataframe.
"""

import json
import logging

import pandas as pd

LOGGER = logging.getLogger(__name__)


def read_polaris_data(json_path):
    """
        Read a JSON file and creates a pandas dataframe out of it.

        :param json_path: File path for the input json file.
        :return: Pandas dataframe with all frames fields values
    """
    dataframe = None

    try:
        with open(json_path, "r") as json_file:
            # converting frames to pandas compatible records
            json_data = json.load(json_file)
            json_records = records_from_satnogs_frames(json_data)

            # Creating a pandas dataframe
            dataframe = pd.DataFrame(json_records)
            dataframe.time = pd.to_datetime(dataframe.time, unit="s")
            dataframe.index = dataframe.time

            # Keep numeric values only
            dataframe = dataframe.select_dtypes(include=['number', 'datetime'])
    except FileNotFoundError as exception_error:
        LOGGER.warning(exception_error)

    return dataframe


def records_from_satnogs_frames(json_data):
    """
        Records that can be read as following format by pandas:
        '[{"col 1":"a","col 2":"b"},{"col 1":"c","col 2":"d"}]'

        :param json_data: polaris fetch format for normalized frames
    """

    records = []

    for frame in json_data["frames"]:
        # reset current record (row)
        this_record = {}

        # scan all fields
        for field in frame["fields"]:
            this_record[field] = frame["fields"][field]["value"]

        # check if we had the time information from frame
        # if not we use the metadata
        if "time" not in this_record:
            this_record["time"] = frame["time"]
        records.append(this_record)

    return records
