# Space weather

This project collects space weather data from ftp.swpc.noaa.gov for your use

Currently the project supports the following indices for a complete year/quarter:

* DGD (Daily Geomagnetic Data)
* DSD (Daily Solar Data)
* DPD (Daily Particle Data)

All of the above are daily indices and are accessible at <ftp://ftp.swpc.noaa.gov/pub/indices/old_indices/>.

It also supports strorage and propagation of TLEs, OMMs which are fetched from
<https://celestrak.com/>.

We went with celestrak because their license permits storage, modification and
redistribution of the data (permissive) as against Space-Track who have a
non-permissive license (which would make this project illegal).

Feel free to [read this blog](https://libre.space/2020/03/02/space-situational-awareness/)
by LSF to learn more.

The project structure is like so:

``` bash
vinvelivaanilai
├── orbit
│   ├── predict_orbit.py (uses TLEs/OMMs to predict/propagate orbit)
│   └── tle_fetch.py (fetches TLEs from celestrak)
├── space_weather
│   ├── sw_extractor.py (extracts space-weather data from SWPC files)
│   └── sw_file_fetch.py (fetches files with the indices from SWPC)
└── storage
    ├── idb_config.py (configuration of influxdb)
    ├── retrieve.py (retrieves data from influxdb)
    ├── store.py (pushes data to influxdb)
    └── docker-compose.yml (fire up influxdb)
```

## Installation

You can install vinvelivaanilai using pip

``` BASH
pip install vinvelivaanilai
```

It is recommended that you install the project in a virtual environment as it
is still under development.

To create a virtual environment and install in it, run:

``` BASH
python -m venv .venv
source .venv/bin/activate
pythom -m pip install vinvelivaanilai
```

To install an editable version of the master branch:

``` BASH
git clone https://gitlab.com/librespacefoundation/polaris/vinvelivaanilai.git
cd vinvelivaanilai
pip install -e .
```

## Usage

For fetching indices from SWPC

``` BASH
(.venv) $ python

>>> from polaris.swpc.space_weather.sw_file_fetch import fetch_indices

>>> from polaris.swpc.space_weather.sw_extractor import extract_data_regex

>>> import datetime

>>> start_date = datetime.datetime(year=2018, month=1, day=30)

>>> final_date = datetime.datetime(year=2019, month=2, day=28)

>>> fetch_indices("DGD", start_date, final_date)

>>> df = extract_data_regex("DGD", "2018_DGD.txt")

>>> df
            Fredericksburg A  Fredericksburg K 0-3  Fredericksburg K 3-6  ...  Planetary K 15-18  Planetary K 18-21  Planetary K 21-24
Date                                                                      ...
2018-01-01                 8                     3                     3  ...                  1                  1                  1
2018-01-02                 4                     1                     1  ...                  1                  2                  1
2018-01-03                 3                     0                     1  ...                  1                  1                  1
2018-01-04                 3                     1                     0  ...                  0                  2                  1
2018-01-05                 5                     1                     2  ...                  1                  1                  2
...                      ...                   ...                   ...  ...                ...                ...                ...
2018-12-27                 5                     2                     2  ...                  1                  1                  3
2018-12-28                19                     4                     4  ...                  3                  4                  3
2018-12-29                 9                     2                     2  ...                  2                  2                  2
2018-12-30                 7                     1                     3  ...                  3                  2                  2
2018-12-31                 7                     3                     2  ...                  1                  0                  1

[365 rows x 27 columns]
```

For using influxdb, you need to start the docker-container using the
docker-compose file in storage

``` Python
$ cd vinvelivaanilai/storage

$ docker-compose up -d
Creating network "storage_default" with the default driver
Creating storage_influxdb_beta_1 ... done
```

For fetching TLEs/OMMs from celestrak and propagating orbits

``` BASH
(.venv) $ python

>>> from polaris.swpc.orbit import tle_fetch, predict_orbit

>>> from datetime import datetime, timedelta

# Both stores data and serves df
>>> omms = tle_fetch.fetch_latest_omm_from_celestrak("/tmp/cubesats.csv", "cubesat", "w")

>>> omms
                                         OBJECT_NAME  OBJECT_ID  MEAN_MOTION  ECCENTRICITY  ...  REV_AT_EPOCH     BSTAR  MEAN_MOTION_DOT  MEAN_MOTION_DDOT
EPOCH                                                                                       ...
2020-07-02 20:09:35.571520            CUTE-1 (CO-55)  2003-031E    14.222448      0.001022  ...         88228  0.000035     3.400000e-07                 0
2020-07-03 00:17:05.416000     CUBESAT XI-IV (CO-57)  2003-031J    14.218309      0.001031  ...         88218  0.000032     2.800000e-07                 0
2020-07-02 20:43:32.275264              CUBESAT XI-V  2005-043F    14.637798      0.001577  ...         78286  0.000024     7.700000e-07                 0
2020-07-02 19:03:35.927776   CUTE-1.7+APD II (CO-65)  2008-021C    14.884828      0.001464  ...         66022  0.000020     1.340000e-06                 0
2020-07-02 17:06:36.440128                 AAUSAT-II  2008-021F    14.950825      0.001206  ...         66169  0.000025     2.140000e-06                 0
...                                              ...        ...          ...           ...  ...           ...       ...              ...               ...
2020-07-02 14:26:08.321344                     ATL-1  2019-084G    15.799381      0.002551  ...          3284  0.000265     4.997300e-04                 0
2020-07-02 21:36:40.737664                    SMOG-P  2019-084J    15.815692      0.002411  ...          3290  0.000278     5.654500e-04                 0
2020-07-03 05:09:12.485440                DUCHIFAT-3  2019-089C    14.990769      0.000771  ...          3066  0.000020     1.690000e-06                 0
2020-07-02 12:57:28.828000  ORBITAL FACTORY 2 (OF-2)  2019-071C    15.333989      0.001350  ...          2344  0.000035     7.820000e-06                 0
2020-07-03 00:59:05.703136             M2 PATHFINDER  2020-037E    14.911992      0.001170  ...            34 -0.000007    -1.220000e-06                 0

[178 rows x 16 columns]

>>> epoch_time = datetime(year=2020, month=6, day=27, hour=11)

# We are resetting the index because we need the column EPOCH to be present
# while propagating orbit. Both r and v have units. You can remove the unit by using .value
>>> predict_orbit.get_position_velocity_from_omm(epoch_time, omms.reset_index())
{
   't': datetime.datetime(2020, 6, 27, 11, 0),
   'r': <Quantity [6759.32081709, 1754.29279972, 1761.88153199] km>,
   'v': <Quantity [ 2.0339923 , -0.66798429, -7.12138608] km / s>
}

>>> from polaris.swpc.storage import store, retrieve

>>> omms_old = tle_fetch.fetch_from_celestrak_csv("/tmp/cubesats.csv")

>>> measurement_name = "cubesats"

>>> bucket_name = "cubesat_omms"

>>> store.dump_to_influxdb(omms_old, measurement_name, bucket_name)

>>> start_date = datetime.now() - timedelta(days=1)

>>> final_date = datetime.now()

>>> retrieve.fetch_from_influxdb(start_date, end_date, measurement_name, bucket_name)
                                  ARG_OF_PERICENTER     BSTAR CLASSIFICATION_TYPE  ...            OBJECT_NAME RA_OF_ASC_NODE REV_AT_EPOCH
EPOCH                                                                              ...
2020-07-03 05:28:10.223104+00:00            60.3184  0.000013                   U  ...  BRITE-PL2 (HEWELIUSZ)       277.2914        31812
2020-07-03 05:17:42.263584+00:00            52.7698  0.000015                   U  ...          NEE-01 PEGASO       283.9268        38801
2020-07-03 05:09:12.485440+00:00           202.4634  0.000020                   U  ...             DUCHIFAT-3         5.2116         3066
2020-07-03 04:55:49.973728+00:00           158.2870  0.000046                   U  ...              E-ST@R-II       296.0163        22981
2020-07-03 04:50:30.544288+00:00            21.5291  0.000070                   U  ...                KRAKSAT       258.5997         5693
...                                             ...       ...                 ...  ...                    ...            ...          ...
2020-07-02 21:30:20.461888+00:00             7.8141  0.000094                   U  ...             SPACEBEE-1       259.2951        13757
2020-07-02 21:27:51.441760+00:00            68.1632  0.000019                   U  ...            AEROCUBE 5C        97.1618         4358
2020-07-02 21:23:07.163296+00:00           358.6217  0.000072                   U  ...                 MIRATA        96.5183        14150
2020-07-02 21:19:51.643552+00:00           265.9139  0.000039                   U  ...        NAYIF-1 (EO-88)       252.2250        18790
2020-07-02 21:19:31.777600+00:00            73.6534  0.000026                   U  ...                LUCKY-7       146.0457         5490

[85 rows x 16 columns]
```

To know more about any vinvelivaanilai module, use the default python
help function and call the module.

## Credits

A big shout-out to the following projects:

* celestrak <https://celestrak.com/>
* poliastro <https://github.com/poliastro/poliastro>
* orbit-predictor <https://github.com/satellogic/orbit-predictor>
* SWPC <https://www.swpc.noaa.gov/>

and the following people for guiding me:

* Hugh (@SaintAardvark)
* Red (@redsharpbyte)
* Xabi (@crespum)
* Patrick (@DL4PD)
* Juan Luis (@astrojuanlu)

## Work in progress

* ~~pip installation support~~
* ~~TLE extraction and orbit propogation~~
* GEOA data extraction
* SPE (Space Proton Event) data extraction (*)

(*) Some proton events are already covered in DPD data.
