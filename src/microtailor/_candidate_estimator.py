from pydantic import BaseModel, Extra, Field
from abc import ABC, abstractmethod
from typing import Optional
from ._typing_utils import NumArray, Float, IntArray
import numpy as np
import numpy.typing as npt

from ._utils import calc_phase_correlation_matrix

class CandidateEstimator(ABC,BaseModel):
    @abstractmethod
    def __call__(
            self, 
            images : NumArray, 
            pair_indices : IntArray,
            estimated_displacement: NumArray,
            allowed_error: Float,
            ) -> npt.NDArray[np.float_]:
        ...
        

class PhaseCorrelationEstimator(CandidateEstimator):
    num_candidates :int  = Field(5,description="number of candidate points")

    def __call__(self, 
            images : NumArray, 
            pair_indices : IntArray,
            estimated_positions : Optional[NumArray],
            allowed_error: Float,) -> npt.NDArray[np.float_]:
        
        for pair_index in pair_indices:
            images = images[pair_index]
            assert len(images) == 2
            pcm = calc_phase_correlation_matrix(
                images[0],images[1]
            )
            row, col = np.unravel_index(np.argsort(pcm.ravel(),), pcm.shape)


candidate_estimators={
    "phase_correlation" : PhaseCorrelationEstimator,
}