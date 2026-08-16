import dataclasses

import pytest

from app.models.network import Node, RoadNetwork


def test_node_and_edge_are_frozen(real_network: RoadNetwork):
    node = real_network.nodes[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        node.name = "Changed"
    edge = real_network.edges[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        edge.bumpiness = 0.0


def test_from_json_loads_real_network(real_network: RoadNetwork):
    assert len(real_network.nodes) == 21
    assert len(real_network.edges) == 36


def test_haversine_km_symmetric_and_self_zero(real_network: RoadNetwork):
    assert real_network.haversine_km(20, 17) == real_network.haversine_km(17, 20)
    assert real_network.haversine_km(5, 5) == 0.0


def test_haversine_km_pinned_values(real_network: RoadNetwork):
    assert real_network.haversine_km(20, 17) == pytest.approx(52.1211)


def test_get_neighbors_excludes_blocked(real_network: RoadNetwork):
    neighbors_19 = [nb for nb, _ in real_network.get_neighbors(19)]
    neighbors_11 = [nb for nb, _ in real_network.get_neighbors(11)]
    neighbors_3 = [nb for nb, _ in real_network.get_neighbors(3)]
    neighbors_9 = [nb for nb, _ in real_network.get_neighbors(9)]
    assert 11 not in neighbors_19
    assert 19 not in neighbors_11
    assert 9 not in neighbors_3
    assert 3 not in neighbors_9
    # the raw adjacency list still contains the blocked edge; only get_neighbors filters it
    assert 11 in [nb for nb, _ in real_network.graph[19]]


def test_get_all_edges_count_and_uniqueness(real_network: RoadNetwork):
    edges = real_network.get_all_edges()
    assert len(edges) == 36
    assert all(isinstance(e, frozenset) and len(e) == 2 for e in edges)
    assert len(set(edges)) == 36


def test_get_bumpiness_known_and_default(real_network: RoadNetwork):
    assert real_network.get_bumpiness(frozenset({9, 0})) == 2.0
    assert real_network.get_bumpiness(frozenset({999, 998})) == 5.0


def test_blocked_pairs_bidirectional(real_network: RoadNetwork):
    for pair in [(19, 11), (11, 19), (3, 9), (9, 3)]:
        assert pair in real_network.blocked_pairs
