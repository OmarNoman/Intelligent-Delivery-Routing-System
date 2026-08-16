import pytest

from app.models.network import RoadNetwork
from app.routing.heuristics import haversine_time_heuristic


def test_heuristic_equals_distance_over_ref_speed(real_network: RoadNetwork):
    for node, goal, ref in [(20, 17, 100.0), (0, 14, 80.0)]:
        expected = real_network.haversine_km(node, goal) / ref
        assert haversine_time_heuristic(real_network, node, goal, ref) == pytest.approx(expected)


def test_heuristic_zero_at_goal(real_network: RoadNetwork):
    assert haversine_time_heuristic(real_network, 17, 17, 100.0) == 0.0


def test_heuristic_scales_inversely_with_ref_speed(real_network: RoadNetwork):
    h_100 = haversine_time_heuristic(real_network, 20, 17, 100.0)
    h_200 = haversine_time_heuristic(real_network, 20, 17, 200.0)
    assert h_200 == pytest.approx(h_100 / 2)
