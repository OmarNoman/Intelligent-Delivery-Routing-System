from app.config import Settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.routing.planning import path_time as raw_path_time
from app.routing.replanning import simulate_replanning as raw_simulate_replanning
from app.routing.search import astar_time as raw_astar_time
from app.routing.search import ucs_time as raw_ucs_time
from app.services.routing_service import RoutingService


def test_compute_segment_speeds_covers_all_edges(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    speeds = service.compute_segment_speeds(5)
    assert set(speeds.keys()) == set(real_network.get_all_edges())


def test_apply_constraints_uses_settings_constraint_speed(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, baseline_speeds: dict
):
    custom_settings = Settings(constraint_speed=10.0)
    service = RoutingService(real_network, fuzzy_controller, custom_settings)
    edge = frozenset({20, 4})
    capped = service.apply_constraints(baseline_speeds, {edge})
    assert capped[edge] == 10.0


def test_astar_ucs_path_time_delegate_correctly(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings, baseline_speeds: dict
):
    service = RoutingService(real_network, fuzzy_controller, settings)

    assert service.astar_time(20, 17, baseline_speeds, 100.0) == raw_astar_time(
        real_network, 20, 17, baseline_speeds, 100.0, settings.baseline_speed
    )
    assert service.ucs_time(20, 17, baseline_speeds) == raw_ucs_time(
        real_network, 20, 17, baseline_speeds, settings.baseline_speed
    )
    path = [20, 4, 18]
    assert service.path_time(path, baseline_speeds) == raw_path_time(
        real_network, path, baseline_speeds, settings.baseline_speed
    )


def test_simulate_replanning_delegates_correctly(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings, baseline_speeds: dict
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    constrained_speeds = {k: min(v, settings.constraint_speed) for k, v in baseline_speeds.items()}

    assert service.simulate_replanning(20, 17, baseline_speeds, constrained_speeds) == raw_simulate_replanning(
        real_network, 20, 17, baseline_speeds, constrained_speeds, settings.baseline_speed, settings.replan_fraction
    )
