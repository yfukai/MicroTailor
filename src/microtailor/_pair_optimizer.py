from abc import ABC, abstractmethod
import pandas as pd

class PairOptimizer(ABC):
    @abstractmethod
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

class NormalizedClossCorrelationOptimizer(PairOptimizer):
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

pair_optimizers={
    "normalized_cross_correlation" : NormalizedClossCorrelationOptimizer,
}