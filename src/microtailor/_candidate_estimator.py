from abc import ABC, abstractmethod
from ._typing_utils import NumArray
import numpy as np
import numpy.typing as npt

class CandidateEstimator(ABC):
    @abstractmethod
    def __call__(self, images : NumArray, constraints : NumArray) -> npt.NDArray[np.float_]:
        ...
        

class PhaseCorrelationEstimator(CandidateEstimator):
    def __call__(self, images, constraints) -> npt.NDArray[np.float_]:
        ...

candidate_estimators={
    "phase_correlation" : PhaseCorrelationEstimator,
}