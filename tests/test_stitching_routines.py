from microtailor._stitcher import _calc_overlap_area_ratio, _parse_positions_to_pairs
import numpy as np


def test_calc_overlap_area_ratio() -> None:
    image_shape = (123,456)
    area = np.product(list(image_shape))
    position_overlaps = [
        ([0,0], 123*456),
        ([10,0], 113*456),
        ([0,10], 123*446),
        ([-100,0], 23*456),
        ([0,-100], 123*356),
        ([-123,0], 0),
        ([-200,0], 0),
        ([123,0], 0),
        ([-200,0], 0),
        ([-122,500], 0),
        ([-600,-500], 0),
    ]
    for pos, ol in position_overlaps:
        res = _calc_overlap_area_ratio(image_shape,pos)
        print(res, ol/area, pos)
        assert np.isclose(res,ol/area)

def test_parse_positions_to_pairs_tile_indices() -> None:
    overlap_threshold_percentage = 5
    image_shape = (123,456)

    args = [
        {
            "tile_indices" : [(0,1,0),],
            "estimated_positions" : [],
        }, 
    ]

def test_parse_positions_to_pairs_estimated_positions() -> None:
    overlap_threshold_percentage = 5
    image_shape = (123,456,789)
    estimated_positions = [(-100,-100),()]

