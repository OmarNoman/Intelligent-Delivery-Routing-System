import pytest

from app.models.network import RoadNetwork
from app.routing.planning import apply_constraints, path_distance_km, path_time, sample_constrained_edges


def test_apply_constraints_caps_present_edges(real_network: RoadNetwork, baseline_speeds: dict):
    edge = frozenset({20, 4})
    capped = apply_constraints(baseline_speeds, {edge}, 40.0)
    assert capped[edge] == 40.0

    low_speed_map = dict(baseline_speeds)
    low_speed_map[edge] = 10.0
    capped_low = apply_constraints(low_speed_map, {edge}, 40.0)
    assert capped_low[edge] == 10.0  # already below cap, unchanged


def test_apply_constraints_ignores_missing_edges(baseline_speeds: dict):
    missing_edge = frozenset({9999, 9998})
    capped = apply_constraints(baseline_speeds, {missing_edge}, 40.0)
    assert capped == baseline_speeds
    assert capped is not baseline_speeds  # returns a copy, doesn't mutate input


def test_path_time_none_and_single_node(real_network: RoadNetwork, baseline_speeds: dict):
    assert path_time(real_network, None, baseline_speeds, 100.0) == 0.0
    assert path_time(real_network, [20], baseline_speeds, 100.0) == 0.0


def test_path_time_matches_manual_sum(real_network: RoadNetwork, baseline_speeds: dict):
    path = [20, 4, 18]
    expected = sum(
        real_network.haversine_km(path[i], path[i + 1])
        / baseline_speeds.get(frozenset({path[i], path[i + 1]}), 100.0)
        for i in range(len(path) - 1)
    )
    assert path_time(real_network, path, baseline_speeds, 100.0) == pytest.approx(expected)


def test_path_distance_km_none_and_single_node(real_network: RoadNetwork):
    assert path_distance_km(real_network, None) == 0.0
    assert path_distance_km(real_network, [20]) == 0.0


def test_path_distance_km_matches_manual_sum(real_network: RoadNetwork):
    path = [20, 4, 18]
    expected = sum(real_network.haversine_km(path[i], path[i + 1]) for i in range(len(path) - 1))
    assert path_distance_km(real_network, path) == pytest.approx(expected)


def test_sample_constrained_edges_deterministic_and_correct_size(real_network: RoadNetwork):
    all_edges = real_network.get_all_edges()
    sampled = sample_constrained_edges(real_network, 0.60, seed=42)
    assert len(sampled) == round(0.60 * len(all_edges))
    assert sampled.issubset(set(all_edges))
    assert sample_constrained_edges(real_network, 0.60, seed=42) == sampled  # same seed -> same sample
    assert sample_constrained_edges(real_network, 0.60, seed=1) != sampled  # different seed -> (almost certainly) different
