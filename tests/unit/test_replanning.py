import pytest

from app.models.network import RoadNetwork
from app.routing.replanning import simulate_replanning


def test_no_initial_path_returns_error_dict(disconnected_network: RoadNetwork):
    speeds = {frozenset(e): 50.0 for e in disconnected_network.get_all_edges()}
    result = simulate_replanning(disconnected_network, 0, 2, speeds, speeds, 50.0, 0.20)
    assert result == {"error": "No initial path found"}


def test_pinned_baseline_replanning_result(real_network: RoadNetwork, baseline_speeds: dict):
    constrained_speeds = {k: min(v, 40.0) for k, v in baseline_speeds.items()}
    result = simulate_replanning(real_network, 20, 17, baseline_speeds, constrained_speeds, 100.0, 0.20)

    assert result["trigger_node"] == 4
    assert result["trigger_idx"] == 1
    assert result["nodes_exp"] == 23
    assert result["total_time_h"] == pytest.approx(1.401702)
    assert result["full_path"] == result["init_path"]


def test_trigger_idx_clamped_for_extreme_fractions(real_network: RoadNetwork, baseline_speeds: dict):
    result_high = simulate_replanning(real_network, 20, 17, baseline_speeds, baseline_speeds, 100.0, 0.99)
    init_len = len(result_high["init_path"])
    assert result_high["trigger_idx"] == init_len - 2

    result_low = simulate_replanning(real_network, 20, 17, baseline_speeds, baseline_speeds, 100.0, 0.0001)
    assert result_low["trigger_idx"] == 0
