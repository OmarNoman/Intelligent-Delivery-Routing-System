import math

from hypothesis import given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from app.config import get_settings
from app.models.network import RoadNetwork
from app.routing.heuristics import haversine_time_heuristic
from app.routing.search import ucs_time

_SETTINGS = get_settings()
_NETWORK = RoadNetwork.from_json(_SETTINGS.network_data_path)
_EDGES = _NETWORK.get_all_edges()
_NODE_IDS = sorted(_NETWORK.nodes.keys())

_speed = st.floats(min_value=1.0, max_value=150.0, allow_nan=False, allow_infinity=False)
_speed_map = st.lists(_speed, min_size=len(_EDGES), max_size=len(_EDGES)).map(
    lambda speeds: dict(zip(_EDGES, speeds))
)


@hyp_settings(max_examples=100, deadline=None)
@given(speed_map=_speed_map, goal=st.sampled_from(_NODE_IDS))
def test_heuristic_never_overestimates_true_cost(speed_map, goal):
    baseline = 100.0
    max_speed_ref = max(speed_map.values())

    for node in _NODE_IDS:
        if node == goal:
            continue
        h = haversine_time_heuristic(_NETWORK, node, goal, max_speed_ref)
        _, h_star, _ = ucs_time(_NETWORK, node, goal, speed_map, baseline)
        if math.isinf(h_star):
            continue  # unreachable from this node under this random speed map: vacuously admissible
        assert h <= h_star + 1e-9
