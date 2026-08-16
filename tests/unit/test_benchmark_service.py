import pytest

from app.config import Settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.services.benchmark_service import (
    BenchmarkResult,
    default_profiles,
    run_full_sweep,
    summarize,
)
from app.services.routing_service import RoutingService


def test_default_profiles_cover_all_edges(
    real_network: RoadNetwork, fuzzy_controller: FuzzySpeedController, settings: Settings
):
    service = RoutingService(real_network, fuzzy_controller, settings)
    profiles = default_profiles(real_network, service, settings)

    assert len(profiles) == 4
    names = {p.name for p in profiles}
    assert names == {"flat_100kmh", "fis_fragility_2", "fis_fragility_5", "fis_fragility_8"}
    for p in profiles:
        assert set(p.segment_speeds.keys()) == set(real_network.get_all_edges())


def test_run_full_sweep_reproduces_baseline_golden_values(real_network: RoadNetwork, settings: Settings):
    flat_profile = default_profiles(
        real_network,
        RoutingService(real_network, FuzzySpeedController(), settings),
        settings,
    )[0]
    assert flat_profile.name == "flat_100kmh"

    results = run_full_sweep(real_network, [flat_profile], settings.baseline_speed)
    original = next(r for r in results if r.start == 20 and r.goal == 17)

    assert original.ucs_nodes_expanded == 19
    assert original.astar_nodes_expanded == 12
    assert original.costs_agree is True


def test_run_full_sweep_covers_all_ordered_pairs(real_network: RoadNetwork, baseline_speeds: dict):
    from app.services.benchmark_service import SpeedProfile

    profile = SpeedProfile(name="flat", segment_speeds=baseline_speeds, max_speed_ref=100.0)
    results = run_full_sweep(real_network, [profile], 100.0)

    node_count = len(real_network.nodes)
    assert len(results) == node_count * (node_count - 1)
    assert all(r.costs_agree for r in results)
    assert all(r.start != r.goal for r in results)


def test_summarize_matches_manual_stats():
    results = [
        BenchmarkResult("p", 0, 1, 1.0, 10, 1.0, 5, 50.0, True),
        BenchmarkResult("p", 0, 2, 1.0, 10, 1.0, 7, 30.0, True),
        BenchmarkResult("p", 0, 3, 1.0, 10, 1.0, 6, 40.0, True),
    ]
    summary = summarize(results)
    assert {s.label for s in summary} == {"p", "combined"}

    p_stats = next(s for s in summary if s.label == "p")
    assert p_stats.n == 3
    assert p_stats.mean == pytest.approx(40.0)
    assert p_stats.median == pytest.approx(40.0)
    assert p_stats.minimum == pytest.approx(30.0)
    assert p_stats.maximum == pytest.approx(50.0)
    assert p_stats.stdev == pytest.approx(10.0)
    assert p_stats.ci95_low < p_stats.mean < p_stats.ci95_high
