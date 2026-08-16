import random
import sys
import time
import warnings

warnings.filterwarnings("ignore")  # suppress verbose skfuzzy output

# Windows consoles default to cp1252, which cannot encode characters like
# mu (μ) or <= (≤) used in the console output below and crashes on print().
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config import get_settings
from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.explainability import explain_worked_example
from app.models.cargo import CargoProfile
from app.models.network import RoadNetwork
from app.routing.heuristics import haversine_time_heuristic
from app.services.routing_service import RoutingService
from scripts.plotting import (
    path_label,
    plot_control_surface,
    plot_membership_functions,
    plot_route_map,
    plot_task1_route,
    plot_task3_comparison,
    plot_worked_example,
)


def main() -> None:
    settings = get_settings()
    network = RoadNetwork.from_json(settings.network_data_path)
    controller = FuzzySpeedController()
    service = RoutingService(network, controller, settings)

    _run_task1(network, service, settings)
    _run_task2(controller)
    _run_task3(network, service, settings)

    print("\nComplete")


def _run_task1(network: RoadNetwork, service: RoutingService, settings) -> None:
    print("\n" + "=" * 65)
    print("TASK 1 - BASELINE TIME-BASED A* PLANNER")
    print("=" * 65)
    baseline_speeds = {frozenset(e): settings.baseline_speed for e in network.get_all_edges()}

    # UCS and Admissibility
    t0 = time.perf_counter()
    ucs_path, ucs_cost, ucs_exp = service.ucs_time(settings.start_node, settings.goal_node, baseline_speeds)
    t_ucs = time.perf_counter() - t0

    t0 = time.perf_counter()
    ast_path, ast_cost, ast_exp = service.astar_time(
        settings.start_node, settings.goal_node, baseline_speeds, settings.baseline_speed
    )
    t_ast = time.perf_counter() - t0

    violations = 0
    for node in network.nodes:
        if node == settings.goal_node:
            continue
        h = haversine_time_heuristic(network, node, settings.goal_node, settings.baseline_speed)
        h_star = service.ucs_time(node, settings.goal_node, baseline_speeds)[1]
        if h > h_star + 1e-9:
            violations += 1

    print(f"  Route : {network.nodes[settings.start_node].name} -> {network.nodes[settings.goal_node].name}")
    print(f"  Speed : {settings.baseline_speed:.0f} km/h (constant, no FIS)")
    print(f"\n  Admissibility check (h = Haversine / max_speed ≤ h*):")
    print(
        f"  -> Heuristic is {'ADMISSIBLE' if violations == 0 else f'INADMISSIBLE ({violations} violations)'} over all reachable nodes")

    print(f"\n  {'Algorithm':<20} {'Path cost (h)':<16} {'Nodes exp.':<12} {'Time (ms)':<10}")
    print("  " + "-" * 60)
    print(f"  {'UCS (baseline)':<20} {ucs_cost:<16.4f} {ucs_exp:<12} {t_ucs * 1000:.2f}")
    print(f"  {'A* (Haversine)':<20} {ast_cost:<16.4f} {ast_exp:<12} {t_ast * 1000:.2f}")
    print(f"\n  Optimal path ({ast_cost * 60:.1f} min):\n    {path_label(network, ast_path)}")

    print("\n  A* Search Trace:")
    service.astar_time(settings.start_node, settings.goal_node, baseline_speeds, settings.baseline_speed,
                        print_trace=True)
    plot_task1_route(network, ast_path, ast_cost, settings.start_node, settings.goal_node)


def _run_task2(controller: FuzzySpeedController) -> None:
    print("\n" + "=" * 65)
    print("TASK 2 - FUZZY INFERENCE SYSTEM")
    print("=" * 65)

    print("  Inputs : Fragility [0–10], Bumpiness [0–10]")
    print("  Output : Max Safe Speed [40–100] km/h")
    print("  Rules  : 9-rule base (3 fragility × 3 bumpiness levels)")
    print("  Defuzz : Centroid method")

    plot_membership_functions()

    result = explain_worked_example(controller, fragility_val=5.0, bumpiness_val=7.0)
    print("\n" + "=" * 65)
    print("TASK 2 - WORKED EXAMPLE")
    print("=" * 65)
    print(f"  Cargo fragility : {result.fragility_val:.1f}  ->  μ_Moderate = {result.mu_frag_moderate:.3f}")
    print(f"  Road bumpiness  : {result.bumpiness_val:.1f}  ->  μ_Moderate = {result.mu_bump_moderate:.3f}, "
          f"μ_Rough = {result.mu_bump_rough:.3f}")
    print("\n  Active rules (partial activation = genuine ambiguity):")
    print(
        f"    Rule 5  Moderate & Moderate -> Medium : min({result.mu_frag_moderate:.3f}, "
        f"{result.mu_bump_moderate:.3f}) = {result.rule5_strength:.3f}")
    print(
        f"    Rule 6  Moderate & Rough   -> Slow   : min({result.mu_frag_moderate:.3f}, "
        f"{result.mu_bump_rough:.3f}) = {result.rule6_strength:.3f}")
    print(f"\n  Defuzzification (centroid) -> Max Safe Speed = {result.crisp_speed:.2f} km/h")
    print(f"  Interpretation : moderate cargo on a roughish road is capped at ~{result.crisp_speed:.0f} km/h")
    print("=" * 65)
    plot_worked_example(result)

    plot_control_surface(controller)


def _run_task3(network: RoadNetwork, service: RoutingService, settings) -> None:
    print("\n" + "=" * 65)
    print("TASK 3 - INTEGRATION AND COMPARISON")
    print("=" * 65)
    all_edges = network.get_all_edges()
    random.seed(settings.constraint_seed)
    constrained_edges = set(random.sample(all_edges, round(settings.constraint_fraction * len(all_edges))))

    print(f"  Route  : {network.nodes[settings.start_node].name} -> {network.nodes[settings.goal_node].name}")
    print(
        f"  Constraint fraction : {settings.constraint_fraction:.0%} of edges capped at "
        f"{settings.constraint_speed:.0f} km/h  (seed={settings.constraint_seed})")
    print(f"  {len(constrained_edges)} of {len(all_edges)} edges constrained\n")

    task3_results = []
    print(f"  {'Fragility':<11}{'Level':<8}{'Scenario':<28}{'Time (h)':<11}{'Time (min)':<12}{'Nodes exp.'}")
    print("  " + "-" * 78)

    for frag in settings.fragility_levels:
        frag_label = CargoProfile.from_fragility(frag).label
        fis_speeds = service.compute_segment_speeds(frag)
        con_speeds = service.apply_constraints(fis_speeds, constrained_edges)

        pathA, timeA, expA = service.astar_time(
            settings.start_node, settings.goal_node, fis_speeds, max(fis_speeds.values())
        )
        rep = service.simulate_replanning(settings.start_node, settings.goal_node, fis_speeds, con_speeds)
        pathC, timeC, expC = service.astar_time(
            settings.start_node, settings.goal_node, con_speeds, max(con_speeds.values())
        )

        scenarios = [
            ("A - No constraint", pathA, timeA, expA),
            (f"B - Replan at {network.nodes[rep.get('trigger_node', settings.start_node)].name[:10]}",
             rep.get("full_path"), rep.get("total_time_h", float("inf")), rep.get("nodes_exp", 0)),
            ("C - 60% constrained", pathC, timeC, expC),
        ]

        for sc, path, t_h, exp in scenarios:
            task3_results.append(
                {"fragility": frag, "level": frag_label, "scenario": sc, "path": path, "time_h": t_h,
                 "nodes_exp": exp})
            print(f"  {frag:<11}{frag_label:<8}{sc:<28}{t_h:<11.4f}{t_h * 60:<12.2f}{exp}")
        print("  " + "-" * 70)

    print("\n  Path details:")
    for r in task3_results:
        print(f"    [{r['level']} F={r['fragility']}, {r['scenario'][:18]}]")
        print(f"      {path_label(network, r['path'])}")

    for frag in settings.fragility_levels:
        plot_route_map(network, task3_results, frag, constrained_edges, settings.start_node, settings.goal_node)
    plot_task3_comparison(task3_results, settings.fragility_levels)


if __name__ == "__main__":
    main()
