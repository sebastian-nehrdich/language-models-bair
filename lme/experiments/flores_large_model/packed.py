from lme.data_processors.flores200 import Packed2DataProcessor
from lme.model_mixins import MT53BModelMixin

from lme.experiments.flores_large_model.baseline import FloresBaseline1BExperiment


class FloresPacked1BExperiment(FloresBaseline1BExperiment):
    # (2048 / 2) = 1024 // (2 ** 11 / 2 ** 1) = 2 ** 10
    TARGET_TOTAL_BATCH_SIZE_PER_UPDATE = 2 ** 10

    DATA_PROCESSOR_CLASSES = [Packed2DataProcessor]


class FloresPacked3BExperiment(MT53BModelMixin, FloresPacked1BExperiment):
    pass
