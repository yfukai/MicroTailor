from microtailor._stitcher import _calc_overlap_area_ratio
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
