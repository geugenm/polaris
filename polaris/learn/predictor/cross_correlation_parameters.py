"""
Cross Correlation module parameters
"""


# pylint: disable=too-few-public-methods, too-many-arguments
# placeholder class for parameters. Hence,
# only one method and large number of parameters
class CrossCorrelationParameters:
    """ Cross Correlation parameters class
    """
    def __init__(self,
                 dataset_metadata,
                 model_params=None,
                 use_gridsearch=False,
                 xcorr_params=None,
                 force_cpu=False):
        """
            :param model_params: parameters for each model
            :param dataset_metadata: contains the dataset
            metadata
            :param force_cpu: define the use of CPU or GPU
            :param use_gridsearch: specify if gridsearch will be used during
            predictions
        """
        self.dataset_metadata = dataset_metadata
        self.model_params = model_params
        self.xcorr_params = xcorr_params
        self.use_gridsearch = use_gridsearch
        self.force_cpu = force_cpu
