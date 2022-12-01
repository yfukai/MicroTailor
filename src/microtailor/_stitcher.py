from pydantic import BaseModel, Extra, Field
from typing import Union, Optional
from ._global_optimizer import GlobalOptimizer, global_optimizers
from ._typing_utils import NumArray, IntArray

class Stitcher(BaseModel, extra=Extra.forbid):
    """Stitching base class."""

    candidate_picker = Field(
        "sqeuclidean",
        description="The metric for calculating track linking cost. "
        + "See documentation for `scipy.spatial.distance.cdist` for accepted values.",
    )

    position_interpolator = Field(
        "sqeuclidean",
        description="The metric for calculating track linking cost. "
        + "See documentation for `scipy.spatial.distance.cdist` for accepted values.",
    )
 
    position_optimizer = Field(
        "sqeuclidean",
        description="The metric for calculating track linking cost. "
        + "See documentation for `scipy.spatial.distance.cdist` for accepted values.",
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
               allowed_error : float = 10):
        """Calculate stitched positions of mosaic images.

        Parameters
        ----------
        images : NumArray
            The input images. The first dimension corresponds to the mosaic position.
        tile_indices : Optional[IntArray], optional
            The integer index of the tiles. If None, `estimated_positions` must be supplied.
        estimated_positions : Optional[NumArray], optional
            The estimated position of the tiles in pixel. If None, `tile_indices` must be supplied.
        allowed_error : float, optional
            The allowed error from the `estimated_positions` in pixel, by default 10.
        """

        if tile_indices is None and estimated_positions is None:
            raise ValueError("tile_indices and estimted_positions must not be None at the same time.")

        # construct the initial dataframe and 
        image_pair_df = pd.DataFrame()
       
        position_candidates = self.candidate_picker(images, coordinate_df["tile_pos"], coordinate_df[""])
        coordinate_df["position_candidate"] = position_candidates

        interpolated_positions = self.position_interpolator(images, coordinate_df)
        coordinate_df["interpolated_positions"] = interpolated_positions

        optimized_positions = self.position_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions

        optimized_positions = self.position_optimizer(images, coordinate_df)
        coordinate_df["optimized_positions"] = optimized_positions