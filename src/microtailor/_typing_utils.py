from typing import Union

import numpy as np
import numpy.typing as npt

NumArray = npt.NDArray[Union[np.float_, np.int_]]
FloatArray = npt.NDArray[np.float_]
IntArray = npt.NDArray[np.int_]

Int = Union[int, np.int_]
Float = Union[float, np.float_]