# Polaris learning module

## Predictor: XCorr

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
