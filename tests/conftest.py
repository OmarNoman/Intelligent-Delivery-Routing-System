import pytest

from app.config import Settings, get_settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import Edge, Node, RoadNetwork


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def real_network(settings: Settings) -> RoadNetwork:
    return RoadNetwork.from_json(settings.network_data_path)


@pytest.fixture(scope="session")
def fuzzy_controller() -> FuzzySpeedController:
    return FuzzySpeedController()


@pytest.fixture(scope="session")
def baseline_speeds(real_network: RoadNetwork, settings: Settings) -> dict:
    return {frozenset(e): settings.baseline_speed for e in real_network.get_all_edges()}


@pytest.fixture
def disconnected_network() -> RoadNetwork:
    # Two isolated 2-node components: {0, 1} and {2, 3}, no edge between them.
    nodes = {
        0: Node(0, "A", 0.0, 0.0),
        1: Node(1, "B", 0.01, 0.0),
        2: Node(2, "C", 1.0, 1.0),
        3: Node(3, "D", 1.01, 1.0),
    }
    edges = [
        Edge(0, 1, 2.0, False),
        Edge(2, 3, 2.0, False),
    ]
    return RoadNetwork(nodes, edges)
