from pydantic import BaseModel, Extra, Field
import pandas as pd
import numpy as np
from itertools import combinations
from typing import Union, Optional, List
from ._candidate_estimator import CandidateEstimator, candidate_estimators
from ._position_interpolator import PositionInterpolator, position_interpolators
from ._pair_optimizer import PairOptimizer, pair_optimizers
from ._global_optimizer import GlobalOptimizer, global_optimizers
from ._typing_utils import NumArray, IntArray, Int

def _calc_overlap_area_ratio(image_shape,relative_pos):
    """Calculate the image overlap area ratio with respect to the image area.
    
    """
    percentage = 1.
    for s, p in zip(image_shape,relative_pos):
        percentage *= np.clip(1-np.abs(p/s),0,None)
        print(p,s,percentage)
    return percentage


def _parse_positions_to_pairs(
    image_shape : List[Int],
    tile_indices : Optional[IntArray] = None, 
    estimated_positions : Optional[NumArray] = None,
    overlap_threshold : float = 5,
    ):
    """Parse image positions to image pairs.

    Parameters
    ----------
    image_shape : List[Int]
        The shape of a single input image.
    tile_indices : Optional[IntArray], optional
        The integer index of the tiles. If None, `estimated_positions` must be supplied.
    estimated_positions : Optional[NumArray], optional
        The estimated position of the tiles in pixel. If None, `tile_indices` must be supplied.
    overlap_threshold : float, optional
        The area percentage threshold to calculate pair displacement between tiles. Effective only when tile_indices is None.
    """

    if tile_indices is None and estimated_positions is None:
        raise ValueError("tile_indices and estimated_positions must not be None together.")

    image_pairs = []
    if tile_indices is not None:
        for (j1,ind1), (j2,ind2) in combinations(enumerate(tile_indices),2):
            # if the images are the next to each other or at the same position
            if (np.sum(np.abs(ind1 - ind2) == 1) == 1) or np.all(ind1 == ind2): 
                image_pairs.append({
                    "image_index1":j1,
                    "image_index2":j2,
                    "index_displacement":ind2-ind1,
                    "estimated_displacement":estimated_positions[j2]-estimated_positions[j1]
                }) # image 2 position with respect to image 1
    else:
        for (j1,pos1), (j2,pos2) in combinations(enumerate(estimated_positions),2):
            if _calc_overlap_area_ratio(image_shape,np.array(pos2)-np.array(pos1)) > overlap_threshold:
                image_pairs.append({
                    "image_index1":j1,
                    "image_index2":j2,
                    "estimated_displacement":pos2-pos1
                })

    return pd.DataFrame.from_records(image_pairs)
   

class Stitcher(BaseModel, extra=Extra.forbid, arbitrary_types_allowed = True):
    """Stitching base class."""

    candidate_estimator : Union[str,CandidateEstimator] = Field(
        "phase correlation",
        description="The pair position estimation method. "
        + f"Must be in [{','.join(candidate_estimators.keys())}] or a GlobalOptimizer instance."
    )

    position_interpolator : Union[str,PositionInterpolator] = Field(
        "elliptic_envelope",
        description="The pair displacement filtering and interpolation method. "
        + f"Must be in [{','.join(position_interpolators.keys())}] or a GlobalOptimizer instance."
    )
 
    pair_optimizer : Union[str,GlobalOptimizer] = Field(
        "normalized_cross_correlation",
        description="The pair position optimization method. "
        + f"Must be in [{','.join(pair_optimizers.keys())}] or a GlobalOptimizer instance."
    )

    global_optimizer : Union[str,GlobalOptimizer] = Field(
        "elastic",
        description="The global stage position optimization method. "
        + f"Must be in [{','.join(global_optimizers.keys())}] or a GlobalOptimizer instance."
    )

    def stitch(self, 
               images : NumArray, 
               tile_indices : Optional[IntArray] = None, 
               estimated_positions : Optional[NumArray] = None,
               overlap_threshold : float = 5,
               allowed_error : float = 20):
        """Calculate stitched positions of mosaic images.

        Parameters
        ----------
        images : NumArray
            The input images. The first dimension corresponds to the mosaic position.
        tile_indices : Optional[IntArray], optional
            The integer index of the tiles. If None, `estimated_positions` must be supplied.
        estimated_positions : Optional[NumArray], optional
            The estimated position of the tiles in pixel. If None, `tile_indices` must be supplied.
        overlap_threshold : float, optional
            The area percentage threshold to calculate pair displacement between tiles. Effective only when tile_indices is None.
        allowed_error : float, optional
            The allowed error from the `estimated_positions` in pixel, by default 20.
        """

        if tile_indices is None and estimated_positions is None:
            raise ValueError("tile_indices and estimted_positions must not be None at the same time.")

        # construct the initial dataframe

        

           
       
        position_candidates = self.candidate_picker(images, image_pair_indices)
        coordinate_df["position_candidate"] = position_candidates

        interpolated_positions = self.position_interpolator(images, coordinate_df)
        coordinate_df["interpolated_positions"] = interpolated_positions

        optimized_positions = self.pair_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions

        optimized_positions = self.pair_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions