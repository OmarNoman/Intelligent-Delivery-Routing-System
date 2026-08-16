import math

import pytest

from app.models.network import RoadNetwork
from app.routing.search import astar_time, ucs_time

BASELINE_PATH = [20, 4, 18, 9, 0, 14, 13, 17]


def test_astar_and_ucs_agree_on_baseline_pinned(real_network: RoadNetwork, baseline_speeds: dict):
    ucs_path, ucs_cost, ucs_exp = ucs_time(real_network, 20, 17, baseline_speeds, 100.0)
    assert ucs_path == BASELINE_PATH
    assert ucs_cost == pytest.approx(0.601077)
    assert ucs_exp == 19

    ast_path, ast_cost, ast_exp = astar_time(real_network, 20, 17, baseline_speeds, 100.0, 100.0)
    assert ast_path == BASELINE_PATH
    assert ast_cost == pytest.approx(0.601077)
    assert ast_exp == 12


def test_start_equals_goal_trivial(real_network: RoadNetwork, baseline_speeds: dict):
    assert astar_time(real_network, 20, 20, baseline_speeds, 100.0, 100.0) == ([20], 0.0, 0)
    assert ucs_time(real_network, 20, 20, baseline_speeds, 100.0) == ([20], 0.0, 0)


def test_unreachable_goal_returns_none(disconnected_network: RoadNetwork):
    speeds = {frozenset(e): 50.0 for e in disconnected_network.get_all_edges()}
    path, cost, exp = astar_time(disconnected_network, 0, 2, speeds, 50.0, 50.0)
    assert path is None
    assert math.isinf(cost)

    path, cost, exp = ucs_time(disconnected_network, 0, 2, speeds, 50.0)
    assert path is None
    assert math.isinf(cost)


def test_print_trace_does_not_raise(real_network: RoadNetwork, baseline_speeds: dict, capsys):
    astar_time(real_network, 20, 17, baseline_speeds, 100.0, 100.0, print_trace=True)
    captured = capsys.readouterr()
    assert "Trace ->" in captured.out
