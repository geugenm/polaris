:gitlab_url: https://gitlab.com/librespacefoundation/polaris/vinvelivaanilai/docs/source/getting_started.rst

Getting Started
===============

Installation
------------

Vinvelivaanilai is distributed through PyPI. You can install it using::

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ python -m pip install vinvelivaanilai

You can also install it directly from source::

    $ git clone https://gitlab.com/librespacefoundation/polaris/vinvelivaanilai.git
    $ cd vinvelivaanilai
    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install .

Developers use::

    $ pip install -e .  # Instead of pip install .

You also need to get the
`docker-compose file <https://gitlab.com/librespacefoundation/polaris/vinvelivaanilai/vinvelivaanilai/storage/docker-compose.yml>`_
and run::

    $ docker-compose up

in the directory where the docker-compose file is stored.


Usage
-----

Fetching indices from SWPC is as simple as::

    >>> from polaris.swpc.space_weather import sw_file_fetch, sw_extractor
    >>> from datetime import datetime
    >>> start_date = datetime(year=2018, month=1, day=30)
    >>> final_date = datetime(year=2018, month=3, day=30)
    >>> sw_file_fetch.fetch_indices("DGD", start_date, final_date)
    >>> df = sw_extractor.extract_data_regex("DGD", "2018_DGD.txt")
    >>> df
                Fredericksburg A    ...  Planetary K 21-24
    Date                            ...
    2018-01-01                 8    ...                  1
    2018-01-02                 4    ...                  1
    2018-01-03                 3    ...                  1
    2018-01-04                 3    ...                  1
    2018-01-05                 5    ...                  2
    ...                      ...    ...                ...
    2018-12-27                 5    ...                  3
    2018-12-28                19    ...                  3
    2018-12-29                 9    ...                  2
    2018-12-30                 7    ...                  2
    2018-12-31                 7    ...                  1

    [365 rows x 27 columns]


For fetching OMMs and propagating::

    >>> from polaris.swpc.orbit import tle_fetch, predict_orbit
    >>> from polaris.swpc.storage import store, retrieve
    >>> from datetime import datetime, timedelta

    >>> omms = tle_fetch.fetch_latest_omm_from_celestrak("/tmp/cubesats.csv", "cubesat", "w")
    >>> omms

                                ...  MEAN_MOTION_DDOT
    EPOCH                       ...
    2020-07-02 20:09:35.571520  ...                 0
    2020-07-03 00:17:05.416000  ...                 0
    2020-07-02 20:43:32.275264  ...                 0
    2020-07-02 19:03:35.927776  ...                 0
    2020-07-02 17:06:36.440128  ...                 0
    ...                         ...               ...
    2020-07-02 14:26:08.321344  ...                 0
    2020-07-02 21:36:40.737664  ...                 0
    2020-07-03 05:09:12.485440  ...                 0
    2020-07-02 12:57:28.828000  ...                 0
    2020-07-03 00:59:05.703136  ...                 0

    [178 rows x 16 columns]

    >>> epoch_time = datetime(year=2020, month=6, day=27, hour=11)

    # Retrieves for CUTE-1
    >>> predict_orbit.get_position_velocity_from_omm(epoch_time, omms.reset_index())
    {
        't': datetime.datetime(2020, 6, 27, 11, 0),
        'r': <Quantity [6759.32081709, 1754.29279972, 1761.88153199] km>,
        'v': <Quantity [ 2.0339923 , -0.66798429, -7.12138608] km / s>
    }

    >>> omms_old = tle_fetch.fetch_from_celestrak_csv("/tmp/cubesats.csv")

    >>> measurement_name = "cubesats"
    >>> bucket_name = "cubesat_omms"
    >>> store.dump_to_influxdb(omms_old, measurement_name, bucket_name)
    >>> start_date = datetime.now() - timedelta(days=1)

    >>> final_date = datetime.now()

    >>> retrieve.fetch_from_influxdb(start_date, end_date, measurement_name, bucket_name)
                                      ... RA_OF_ASC_NODE REV_AT_EPOCH
    EPOCH                             ...
    2020-07-03 05:28:10.223104+00:00  ...       277.2914        31812
    2020-07-03 05:17:42.263584+00:00  ...       283.9268        38801
    2020-07-03 05:09:12.485440+00:00  ...         5.2116         3066
    2020-07-03 04:55:49.973728+00:00  ...       296.0163        22981
    2020-07-03 04:50:30.544288+00:00  ...       258.5997         5693
    ...                               ...            ...          ...
    2020-07-02 21:30:20.461888+00:00  ...       259.2951        13757
    2020-07-02 21:27:51.441760+00:00  ...        97.1618         4358
    2020-07-02 21:23:07.163296+00:00  ...        96.5183        14150
    2020-07-02 21:19:51.643552+00:00  ...       252.2250        18790
    2020-07-02 21:19:31.777600+00:00  ...       146.0457         5490

    [85 rows x 16 columns]
