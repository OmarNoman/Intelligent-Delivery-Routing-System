import math

import pytest
from hypothesis import assume, given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from app.config import get_settings
from app.models.network import RoadNetwork
from app.routing.search import astar_time, ucs_time

_SETTINGS = get_settings()
_NETWORK = RoadNetwork.from_json(_SETTINGS.network_data_path)
_EDGES = _NETWORK.get_all_edges()
_NODE_IDS = sorted(_NETWORK.nodes.keys())

_speed = st.floats(min_value=1.0, max_value=150.0, allow_nan=False, allow_infinity=False)
_speed_map = st.lists(_speed, min_size=len(_EDGES), max_size=len(_EDGES)).map(
    lambda speeds: dict(zip(_EDGES, speeds))
)
_node_pair = st.tuples(st.sampled_from(_NODE_IDS), st.sampled_from(_NODE_IDS))


@hyp_settings(max_examples=200, deadline=None)
@given(speed_map=_speed_map, pair=_node_pair)
def test_astar_matches_ucs_cost(speed_map, pair):
    start, goal = pair
    assume(start != goal)
    baseline = 100.0  # fallback only; every edge is present in speed_map so never used
    max_speed_ref = max(speed_map.values())

    _, ucs_cost, _ = ucs_time(_NETWORK, start, goal, speed_map, baseline)
    _, ast_cost, _ = astar_time(_NETWORK, start, goal, speed_map, max_speed_ref, baseline)

    if math.isinf(ucs_cost):
        assert math.isinf(ast_cost)
    else:
        assert ast_cost == pytest.approx(ucs_cost, rel=1e-9, abs=1e-9)
