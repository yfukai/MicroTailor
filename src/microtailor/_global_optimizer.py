from abc import ABC, abstractmethod
from enum import Enum

class GlobalOptimizer(ABC):
    @abstractmethod
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

class MaximumSpanningTreeOptimizer(GlobalOptimizer):
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

class ElasticOptimizer(GlobalOptimizer):
    def __init__(self) -> None:
        super().__init__()
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

global_optimizers={
    "maximum_spanning_tree" : MaximumSpanningTreeOptimizer,
    "elastic" : ElasticOptimizer,
}