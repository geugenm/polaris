:gitlab_url: https://gitlab.com/librespacefoundation/polaris/vinvelivaanilai/docs/source/about.rst

About Vinvelivaanilai
=====================

Vinveli - Space, Vaanilai - Weather (in Tamil)

This project collects space weather data and TLEs from SWPC and celestrak for your use.

Currently the project supports the following indices for a complete year/quarter

* DGD (Daily Geomagnetic Data)
* DSD (Daily Solar Data)
* DPD (Daily Particle Data)

All of the above are daily indices and are accessible at `SWPC. <ftp://ftp.swpc.noaa.gov/pub/indices/old_indices/>`_

It also supports strorage and propagation of TLEs, OMMs which are fetched from
`Celestrak. <https://celestrak.com/>`_

We went with celestrak because their license permits storage, modification and
redistribution of the data (permissive) as against Space-Track who have a
non-permissive license (which would make this project illegal).

Feel free to `read this blog <https://libre.space/2020/03/02/space-situational-awareness/>`_
by LSF to learn more.

The project structure is like so::

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
