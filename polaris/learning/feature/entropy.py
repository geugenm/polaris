import numpy as np


def _maxdist(x_i, x_j):
    return max([abs(ua - va) for ua, va in zip(x_i, x_j)])


def sample_entropy(timeseries_data, run_data_length, filtering_level):
    """
    Utility function to calculate the sample entropy which is
    similar to approximate entropy but it is more consistent in
    estimating the complexity even for small time series
    """

    def _phi(run_data_length):
        x = [[
            timeseries_data[j] for j in range(i, i + run_data_length - 1 + 1)
        ] for i in range(N - run_data_length + 1)]
        C = [
            len([
                1 for j in range(len(x))
                if i != j and _maxdist(x[i], x[j]) <= filtering_level
            ]) for i in range(len(x))
        ]
        return sum(C)

    N = len(timeseries_data)
    return -np.log(_phi(run_data_length + 1) / _phi(run_data_length))


def approximate_entropy(timeseries_data, run_data_length, filtering_level):
    """
    Utility function to calculate the approximate entropy which quantify the
    regularity and unpredictability of the fluctuations in time series data.
    """

    def _phi(run_data_length):
        x = [[
            timeseries_data[j] for j in range(i, i + run_data_length - 1 + 1)
        ] for i in range(N - run_data_length + 1)]
        C = [
            len([1 for x_j in x if _maxdist(x_i, x_j) <= filtering_level]) /
            (N - run_data_length + 1.0) for x_i in x
        ]
        return (N - run_data_length + 1.0)**(-1) * sum(np.log(C))

    N = len(timeseries_data)
    return abs(_phi(run_data_length + 1) - _phi(run_data_length))
