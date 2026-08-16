import heapq
from typing import Callable

from app.models.network import RoadNetwork
from app.routing.heuristics import haversine_time_heuristic


def astar_time(
    network: RoadNetwork,
    start: int,
    goal: int,
    segment_speeds: dict,
    max_speed_ref: float,
    baseline_speed: float,
    heuristic: Callable[[RoadNetwork, int, int, float], float] = haversine_time_heuristic,
    print_trace: bool = False,
) -> tuple:
    # Time-based A* search
    frontier = []
    h0 = heuristic(network, start, goal, max_speed_ref)
    heapq.heappush(frontier, (h0, 0.0, start, [start]))
    explored = set()
    nodes_expanded = 0

    while frontier:
        f, g, node, path = heapq.heappop(frontier)

        if print_trace:
            h = f - g
            node_name = network.nodes[node].name
            print(f"  Trace -> Node: {node_name:<18} | g(n) = {g:<6.3f} | h(n) = {h:<6.3f} | f(n) = {f:<6.3f}")

        if node == goal:
            return path, g, nodes_expanded

        if node in explored:
            continue
        explored.add(node)
        nodes_expanded += 1

        for nb, dist_km in network.get_neighbors(node):
            if nb not in explored:
                spd = segment_speeds.get(frozenset({node, nb}), baseline_speed)
                step_cost = dist_km / spd
                new_g = g + step_cost
                new_h = heuristic(network, nb, goal, max_speed_ref)
                heapq.heappush(frontier, (new_g + new_h, new_g, nb, path + [nb]))

    return None, float("inf"), nodes_expanded


def ucs_time(network: RoadNetwork, start: int, goal: int, segment_speeds: dict, baseline_speed: float) -> tuple:
    # The Uniform Cost Search baseline
    frontier = [(0.0, start, [start])]
    explored = set()
    cost_so_far = {start: 0.0}
    nodes_expanded = 0

    while frontier:
        cost, node, path = heapq.heappop(frontier)

        if node == goal:
            return path, cost, nodes_expanded

        if node in explored:
            continue
        explored.add(node)
        nodes_expanded += 1

        for nb, dist_km in network.get_neighbors(node):
            spd = segment_speeds.get(frozenset({node, nb}), baseline_speed)
            new_cost = cost + dist_km / spd
            if nb not in cost_so_far or new_cost < cost_so_far[nb]:
                cost_so_far[nb] = new_cost
                heapq.heappush(frontier, (new_cost, nb, path + [nb]))

    return None, float("inf"), nodes_expanded
