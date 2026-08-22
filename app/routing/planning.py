import random

from app.models.network import RoadNetwork


def sample_constrained_edges(network: RoadNetwork, fraction: float, seed: int) -> set:
    # Deterministically samples the given fraction of edges to cap, given a seed
    all_edges = network.get_all_edges()
    rng = random.Random(seed)
    return set(rng.sample(all_edges, round(fraction * len(all_edges))))


def apply_constraints(segment_speeds: dict, constrained_edges: set, cap_speed: float) -> dict:
    # Caps the specific edges to cap_speed
    capped = dict(segment_speeds)
    for edge_fs in constrained_edges:
        if edge_fs in capped:
            capped[edge_fs] = min(capped[edge_fs], cap_speed)
    return capped


def path_time(network: RoadNetwork, path: list, speeds: dict, baseline_speed: float) -> float:
    # Calculates the total travel time for a specific path
    if path is None or len(path) < 2:
        return 0.0
    return sum(
        network.haversine_km(path[i], path[i + 1]) /
        speeds.get(frozenset({path[i], path[i + 1]}), baseline_speed)
        for i in range(len(path) - 1)
    )


def path_distance_km(network: RoadNetwork, path: list) -> float:
    # Calculates the total geodesic distance for a specific path
    if path is None or len(path) < 2:
        return 0.0
    return sum(network.haversine_km(path[i], path[i + 1]) for i in range(len(path) - 1))
