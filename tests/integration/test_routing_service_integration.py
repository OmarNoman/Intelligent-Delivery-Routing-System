import pytest

from app.config import Settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.routing.heuristics import haversine_time_heuristic
from app.services.routing_service import RoutingService

BASELINE_PATH = [20, 4, 18, 9, 0, 14, 13, 17]


def test_full_service_baseline_end_to_end(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings, baseline_speeds: dict
):
    service = RoutingService(real_network, fuzzy_controller, settings)

    ucs_path, ucs_cost, ucs_exp = service.ucs_time(settings.start_node, settings.goal_node, baseline_speeds)
    assert ucs_path == BASELINE_PATH
    assert ucs_cost == pytest.approx(0.601077)
    assert ucs_exp == 19

    ast_path, ast_cost, ast_exp = service.astar_time(
        settings.start_node, settings.goal_node, baseline_speeds, settings.baseline_speed
    )
    assert ast_path == BASELINE_PATH
    assert ast_cost == pytest.approx(0.601077)
    assert ast_exp == 12


def test_admissibility_holds_for_baseline_scenario(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings, baseline_speeds: dict
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    violations = 0
    for node in real_network.nodes:
        if node == settings.goal_node:
            continue
        h = haversine_time_heuristic(real_network, node, settings.goal_node, settings.baseline_speed)
        h_star = service.ucs_time(node, settings.goal_node, baseline_speeds)[1]
        if h > h_star + 1e-9:
            violations += 1
    assert violations == 0


def test_full_service_fuzzy_scenario_pinned(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    fis_speeds = service.compute_segment_speeds(5)
    path, cost, exp = service.astar_time(
        settings.start_node, settings.goal_node, fis_speeds, max(fis_speeds.values())
    )
    assert path == BASELINE_PATH
    assert cost == pytest.approx(0.8396122885331007)
    assert exp == 15


def test_simulate_replanning_end_to_end_pinned(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings, baseline_speeds: dict
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    constrained_speeds = {k: min(v, 40.0) for k, v in baseline_speeds.items()}
    result = service.simulate_replanning(settings.start_node, settings.goal_node, baseline_speeds, constrained_speeds)

    assert result["trigger_node"] == 4
    assert result["trigger_idx"] == 1
    assert result["nodes_exp"] == 23
    assert result["total_time_h"] == pytest.approx(1.401702)
    assert result["full_path"] == result["init_path"] == BASELINE_PATH
