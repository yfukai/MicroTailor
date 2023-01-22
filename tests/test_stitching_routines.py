from microtailor._stitcher import _calc_overlap_area_ratio, _parse_positions_to_pairs
import numpy as np
import networkx as nx
import pytest

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
    image_shape = (123,456)

    tile_indices = np.array([(-1,1),(0,1),(1,1),(0,2)])
    edges = [(0,1),(1,2),(1,3)]
    pairs_df = _parse_positions_to_pairs(image_shape,tile_indices)
    pairs_graph = nx.from_edgelist(pairs_df[["image_index1","image_index2"]].values)
    assert nx.is_isomorphic(pairs_graph,nx.from_edgelist(edges)) 

    estimated_positions = np.array([
        (0,0),(11,12),(21,22),(11,412)
    ])
    pairs_df = _parse_positions_to_pairs(image_shape,tile_indices,estimated_positions)
    pairs_graph = nx.from_edgelist(pairs_df[["image_index1","image_index2"]].values)
    assert nx.is_isomorphic(pairs_graph,nx.from_edgelist(edges)) 
    pairs_df = pairs_df.set_index(["image_index1","image_index2"])
    assert np.array_equal(pairs_df.loc[(1,3),"estimated_displacement"],[0,400])
    assert np.array_equal(pairs_df.loc[(1,2),"estimated_displacement"],[10,10])

    tile_indices = np.array([(-1,1,1),(0,1,1),(1,1,1),(0,1,4)])
    with pytest.raises(ValueError):
        pairs_df = _parse_positions_to_pairs(image_shape,tile_indices)
    tile_indices = np.array([(-1,1,1),(0,1,1),(1,1,1),(0,1,4),(0,1,5)])
    with pytest.raises(ValueError):
        pairs_df = _parse_positions_to_pairs(image_shape,tile_indices)

def test_parse_positions_to_pairs_estimated_positions() -> None:
    overlap_threshold_percentage = 5
    image_shape = (123,456,789)
    estimated_positions = np.array([
        (0,0,0),(0,11,12),(10,400,22),(0,11,712)
    ])
    edges = [(0,1),(0,2),(0,3),(1,2),(1,3)]
    pairs_df = _parse_positions_to_pairs(image_shape,
        estimated_positions=estimated_positions,
        overlap_threshold_percentage=overlap_threshold_percentage)
    pairs_graph = nx.from_edgelist(pairs_df[["image_index1","image_index2"]].values)
    assert nx.is_isomorphic(pairs_graph,nx.from_edgelist(edges)) 
 