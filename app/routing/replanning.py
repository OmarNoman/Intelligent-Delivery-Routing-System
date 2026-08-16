import math

from app.models.network import RoadNetwork
from app.routing.planning import path_time
from app.routing.search import astar_time


def simulate_replanning(
    network: RoadNetwork,
    start: int,
    goal: int,
    initial_speeds: dict,
    constrained_speeds: dict,
    baseline_speed: float,
    replan_fraction: float,
) -> dict:
    # The Hybrid architecture pattern: Plan -> Encounter Obstacle -> Replan
    max_spd_init = max(initial_speeds.values())
    max_spd_con = max(constrained_speeds.values())

    # Phase 1: initial plan
    init_path, _, init_exp = astar_time(network, start, goal, initial_speeds, max_spd_init, baseline_speed)
    if init_path is None:
        return {"error": "No initial path found"}

    # Trigger mid-journey recalculation
    trigger_idx = math.ceil(replan_fraction * len(init_path)) - 1
    trigger_idx = max(0, min(trigger_idx, len(init_path) - 2))
    replan_node = init_path[trigger_idx]
    pre_time = path_time(network, init_path[:trigger_idx + 1], initial_speeds, baseline_speed)

    # Phase 2: Replanning from current node
    replan_path, replan_remaining, replan_exp = astar_time(
        network, replan_node, goal, constrained_speeds, max_spd_con, baseline_speed
    )
    if replan_path is None:
        replan_path = [replan_node]
        replan_remaining = float("inf")

    return {
        "init_path": init_path,
        "replan_path": replan_path,
        "full_path": init_path[:trigger_idx + 1] + replan_path[1:],
        "trigger_node": replan_node,
        "trigger_idx": trigger_idx,
        "total_time_h": pre_time + replan_remaining,
        "nodes_exp": init_exp + replan_exp,
    }
