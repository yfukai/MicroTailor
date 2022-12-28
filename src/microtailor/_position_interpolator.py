from abc import ABC, abstractmethod
import pandas as pd

class PositionInterpolator(ABC):
    @abstractmethod
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

class EllipticEnvelopeInterpolator(PositionInterpolator):
    def __call__(self, positions, ) -> pd.DataFrame:
        ...

position_interpolators={
    "elliptic_envelope" : EllipticEnvelopeInterpolator,
}