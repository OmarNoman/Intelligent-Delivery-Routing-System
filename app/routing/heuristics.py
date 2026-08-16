from app.models.network import RoadNetwork


def haversine_time_heuristic(network: RoadNetwork, node: int, goal: int, max_speed_ref: float) -> float:
    # Admissible heuristic: straight-line (haversine) distance / reference max speed
    dist_km = network.haversine_km(node, goal)
    return dist_km / max_speed_ref
