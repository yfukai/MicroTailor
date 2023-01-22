from pydantic import BaseModel, Extra, Field
import pandas as pd
import numpy as np
from itertools import combinations
import networkx as nx
from typing import Union, Optional, List, Dict
from ._candidate_estimator import CandidateEstimator, candidate_estimators
from ._position_interpolator import PositionInterpolator, position_interpolators
from ._pair_optimizer import PairOptimizer, pair_optimizers
from ._global_optimizer import GlobalOptimizer, global_optimizers
from ._typing_utils import NumArray, IntArray, Int, ArgType

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
    overlap_threshold_percentage : float = 5,
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
    overlap_threshold_percentage : float, optional
        The area percentage threshold to calculate pair displacement between tiles. Effective only when tile_indices is None.
    """

    image_pairs = []
    if tile_indices is not None:
        for (j1,ind1), (j2,ind2) in combinations(enumerate(tile_indices),2):
            # if the images are the next to each other or at the same position
            diff = np.abs(ind1 - ind2)
            if ((np.max(diff) == 1 and np.sum(diff == 1) == 1)) or np.all(ind1 == ind2): 
                if estimated_positions is not None:
                    dpos = estimated_positions[j2]-estimated_positions[j1]
                else:
                    dpos = None
                image_pairs.append({
                    "image_index1":j1,
                    "image_index2":j2,
                    "index_displacement":ind2-ind1,
                    "estimated_displacement":dpos,
                }) # image 2 position with respect to image 1
    else:
        for (j1,pos1), (j2,pos2) in combinations(enumerate(estimated_positions),2):
            if _calc_overlap_area_ratio(image_shape,np.array(pos2)-np.array(pos1)) > overlap_threshold_percentage/100:
                image_pairs.append({
                    "image_index1":j1,
                    "image_index2":j2,
                    "index_displacement":None,
                    "estimated_displacement":pos2-pos1
                })
    
    if len(image_pairs) == 0:
        raise RuntimeError("There is no valid image pairs. Please check tile_indices and estimated_positions.")

    pairs_df = pd.DataFrame.from_records(image_pairs)
    pairs_graph = nx.Graph()
    nodes_count = len(estimated_positions if estimated_positions is not None else tile_indices) 
    pairs_graph.add_nodes_from(range(nodes_count))
    pairs_graph.add_edges_from(pairs_df[["image_index1","image_index2"]].values)

    if len(list(nx.connected_components(pairs_graph))) > 1:
        raise ValueError("Parsing positions resulted more than one connected graphs.")

    return pairs_df
   

class Stitcher(BaseModel, extra=Extra.forbid, arbitrary_types_allowed = True):
    """Stitching base class."""

    candidate_estimator : Union[str,CandidateEstimator] = Field(
        "phase_correlation",
        description="The pair position estimation method. "
        + f"Must be in [{','.join(candidate_estimators.keys())}] or a CandidateEstimator instance."
    )
    candidate_estimator_params : Dict[str,ArgType] = Field({},description="The arguments for cendidate_estimator.")

    position_interpolator : Union[str,PositionInterpolator] = Field(
        "elliptic_envelope",
        description="The pair displacement filtering and interpolation method. "
        + f"Must be in [{','.join(position_interpolators.keys())}] or a PositionInterpolator instance."
    )
 
    pair_optimizer : Union[str,PairOptimizer] = Field(
        "normalized_cross_correlation",
        description="The pair position optimization method. "
        + f"Must be in [{','.join(pair_optimizers.keys())}] or a PairOptimizer instance."
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
               overlap_threshold_percentage : float = 5,
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
        overlap_threshold_percentage : float, optional
            The area percentage threshold to calculate pair displacement between tiles. Effective only when tile_indices is None.
        allowed_error : float, optional
            The allowed error from the `estimated_positions` in pixel, by default 20.
        """
        if tile_indices is None and estimated_positions is None:
            raise ValueError("tile_indices and estimated_positions must not be None together.")
        if (tile_indices is not None and estimated_positions is not None) and (len(tile_indices) != len(estimated_positions)):
            raise ValueError("tile_indices and estimated_positions must have the same length.")
        if (estimated_positions is not None) and len(estimated_positions) < 2:
            raise ValueError("estimated_positions must have the length > 1.")
        if tile_indices is not None and tile_indices.shape[1] != len(images.shape[1:]):
            raise ValueError("entries of tile_indices must have the dimension same as the images.")
        if estimated_positions is not None and estimated_positions.shape[1] != len(images.shape[1:]):
            raise ValueError("entries of estimated_positions must have the dimension same as the images.")

        # construct the initial dataframe with entry 
        pairs_df = _parse_positions_to_pairs(
            images.shape[1:],
            tile_indices,
            estimated_positions,
            overlap_threshold_percentage
        )

        pair_indices = pairs_df[["image_index1","image_index2"]].values
        pairs_df["candidate_displacement"], extra_fields = self.candidate_estimator(
            images, 
            pair_indices,
            pairs_df["estimated_displacement"].to_numpy(),
            allowed_error,
        )
        for k, values in extra_fields.items():
            pairs_df[k] = values

        pairs_df["interpolated_displacement"] = self.position_interpolator(
            images, 
            pair_indices,
            pairs_df["candidate_displacement"].to_numpy(),
            pairs_df["estimated_displacement"].to_numpy(),
            allowed_error,
        )

        pairs_df["local_optimized_displacement"] = self.pair_optimizer(
            images, 
            pair_indices,
            pairs_df["interpolated_displacement"].to_numpy(),
            pairs_df["estimated_displacement"].to_numpy(),
            allowed_error,
        )

        pairs_df["global_optimized_position"] = self.global_optimizer(
            images, 
            pair_indices,
            pairs_df["local_optimized_displacement"].to_numpy(),
            pairs_df["estimated_displacement"].to_numpy(),
            allowed_error,
        )