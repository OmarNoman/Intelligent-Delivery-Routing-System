from app.config import Settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.routing.planning import apply_constraints, path_distance_km, path_time, sample_constrained_edges
from app.routing.replanning import simulate_replanning
from app.routing.search import astar_time, ucs_time


class RoutingService:
    # Composes RoadNetwork, FuzzySpeedController, and the routing algorithms into
    # the facade a caller (demo script, future API) actually needs.

    def __init__(self, network: RoadNetwork, controller: FuzzySpeedController, settings: Settings) -> None:
        self.network = network
        self.controller = controller
        self.settings = settings

    def compute_segment_speeds(self, fragility_val: float) -> dict:
        # Generates the fuzzy-informed speed map for all edges
        speeds = {}
        for edge_fs in self.network.get_all_edges():
            bump = self.network.get_bumpiness(edge_fs)
            speeds[edge_fs] = self.controller.get_safe_speed(fragility_val, bump)
        return speeds

    def apply_constraints(self, segment_speeds: dict, constrained_edges: set) -> dict:
        return apply_constraints(segment_speeds, constrained_edges, self.settings.constraint_speed)

    def sample_constrained_edges(self, fraction: float | None = None, seed: int | None = None) -> set:
        return sample_constrained_edges(
            self.network,
            self.settings.constraint_fraction if fraction is None else fraction,
            self.settings.constraint_seed if seed is None else seed,
        )

    def path_time(self, path: list, speeds: dict) -> float:
        return path_time(self.network, path, speeds, self.settings.baseline_speed)

    def path_distance_km(self, path: list) -> float:
        return path_distance_km(self.network, path)

    def astar_time(self, start: int, goal: int, segment_speeds: dict, max_speed_ref: float,
                    print_trace: bool = False) -> tuple:
        return astar_time(
            self.network, start, goal, segment_speeds, max_speed_ref,
            self.settings.baseline_speed, print_trace=print_trace,
        )

    def ucs_time(self, start: int, goal: int, segment_speeds: dict) -> tuple:
        return ucs_time(self.network, start, goal, segment_speeds, self.settings.baseline_speed)

    def simulate_replanning(self, start: int, goal: int, initial_speeds: dict, constrained_speeds: dict) -> dict:
        return simulate_replanning(
            self.network, start, goal, initial_speeds, constrained_speeds,
            self.settings.baseline_speed, self.settings.replan_fraction,
        )
