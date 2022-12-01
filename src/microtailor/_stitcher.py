from pydantic import BaseModel, Extra, Field
from typing import Union, Optional
from ._pair_optimizer import PairOptimizer, pair_optimizers
from ._global_optimizer import GlobalOptimizer, global_optimizers
from ._typing_utils import NumArray, IntArray

class Stitcher(BaseModel, extra=Extra.forbid):
    """Stitching base class."""

    candidate_estimator = Field(
        "normalized_cross_correlation",
        description="The local pair position optimization method. "
        + f"Must be in [{','.join(pair_optimizers.keys())}] or a GlobalOptimizer instance."
    )

    position_interpolator = Field(
        "sqeuclidean",
        description="The metric for calculating track linking cost. "
        + "See documentation for `scipy.spatial.distance.cdist` for accepted values.",
    )
 
    pair_optimizer = Field(
        "normalized_cross_correlation",
        description="The local pair position optimization method. "
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

        # construct the initial dataframe and 

        image_pairs = []
        if tile_indices is not None:
            for ind in tile_indices:
                image_pairs.append({
                    
                })
                
        else:
            
       
        position_candidates = self.candidate_picker(images, image_pair_indices)
        coordinate_df["position_candidate"] = position_candidates

        interpolated_positions = self.position_interpolator(images, coordinate_df)
        coordinate_df["interpolated_positions"] = interpolated_positions

        optimized_positions = self.pair_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions

        optimized_positions = self.pair_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions