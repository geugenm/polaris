Polaris
=======

The goal of this project is to analyze data from the [SatNOGS Network](https://network.satnogs.org/).

Cloning
-------

To clone this repo for the first time, run:

```
git clone --recurse-submodules https://gitlab.com/crespum/polaris.git
```

Installation of dependencies
----------------------------

For developers:
```bash
pip install -r requirements-dev.txt
```

For users:
```bash
pip install -r requirements.txt
```

Running notebooks
-----------------

Run in the top level of this repo:

```bash
jupyter notebook
```

Running source
--------------

```bash
python -m polaris.decode_elfin
```

What it does
------------

 * Parse data from SatNOGS using Kaitai struct
 * Analyze dependencies in satellite telemetry

More info for developers
-------------------------

Building the package
```bash
python setup.py bdist_wheel
```

How-to
------

### Predictor: XCorr

Cross Correlation finder.

```python
import pandas as pd
from polaris.learning import XCorr

correlator = XCorr()

# df = load_my_data(whatever, function, of, yours)

correlator.fit(df)

print(correlator.importances_map)

```

The XCorr class can be incorporated into a Scikit-learn pipeline.
