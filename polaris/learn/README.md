# Polaris learn module

## Miner: FFlat

`FFlat` is a data explorer that analyzes feature importances and iteratively find the most important features.

`FFlat` stands for Feature Flattening.

## Predictor: XCorr

Cross Correlation finder.

```python
import pandas as pd
from polaris.learn import XCorr

correlator = XCorr()

# df = load_my_data(whatever, function, of, yours)

correlator.fit(df)

print(correlator.importances_map)
```

The XCorr class can be incorporated into a Scikit-learn pipeline.
