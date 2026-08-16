import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config import get_settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.services.benchmark_service import default_profiles, run_full_sweep, summarize
from app.services.routing_service import RoutingService

ORIGINAL_CLAIM_START = 20  # Hoppers Crossing
ORIGINAL_CLAIM_GOAL = 17  # Ferntree Gully
ORIGINAL_CLAIM_PROFILE = "flat_100kmh"
ORIGINAL_CLAIM_PCT = 36.8


def main(output_dir: Path = Path("benchmarks/results")) -> None:
    settings = get_settings()
    network = RoadNetwork.from_json(settings.network_data_path)
    controller = FuzzySpeedController()
    service = RoutingService(network, controller, settings)

    profiles = default_profiles(network, service, settings)
    results = run_full_sweep(network, profiles, settings.baseline_speed)

    agreeing = sum(1 for r in results if r.costs_agree)
    if agreeing != len(results):
        raise AssertionError(f"UCS/A* cost mismatch on {len(results) - agreeing} of {len(results)} searches")

    summary = summarize(results)
    node_count = len(network.nodes)
    pair_count = node_count * (node_count - 1)

    print("\n" + "=" * 70)
    print("NODE-EXPANSION REDUCTION BENCHMARK: A* vs UCS")
    print("=" * 70)
    print(f"  Nodes: {node_count}   Ordered pairs: {pair_count}   Profiles: {len(profiles)}   "
          f"Searches: {len(results) * 2}")
    print(f"  Cost agreement (UCS == A*): {agreeing}/{len(results)} pairs PASS")

    print(f"\n  {'Profile':<18}{'N':<7}{'Mean%':<9}{'Median%':<10}{'Stdev%':<9}"
          f"{'Min%':<8}{'Max%':<8}{'95% CI'}")
    print("  " + "-" * 78)
    for s in summary:
        ci = f"[{s.ci95_low:.1f}, {s.ci95_high:.1f}]"
        print(f"  {s.label:<18}{s.n:<7}{s.mean:<9.1f}{s.median:<10.1f}{s.stdev:<9.1f}"
              f"{s.minimum:<8.1f}{s.maximum:<8.1f}{ci}")

    original_row = next(
        (r for r in results
         if r.profile_name == ORIGINAL_CLAIM_PROFILE
         and r.start == ORIGINAL_CLAIM_START
         and r.goal == ORIGINAL_CLAIM_GOAL),
        None,
    )
    if original_row is not None:
        profile_rows = sorted(
            (r.reduction_pct for r in results if r.profile_name == ORIGINAL_CLAIM_PROFILE),
            reverse=True,
        )
        rank = profile_rows.index(original_row.reduction_pct) + 1
        print(f"\n  Original single-sample claim (Hoppers Crossing -> Ferntree Gully, "
              f"flat 100 km/h): {ORIGINAL_CLAIM_PCT}%")
        print(f"  That single pair's measured reduction in this sweep: "
              f"{original_row.reduction_pct:.1f}% (rank {rank}/{len(profile_rows)} in its profile)")

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    csv_path = output_dir / f"benchmark_{timestamp}.csv"
    json_path = output_dir / f"benchmark_{timestamp}.json"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "profile", "start_id", "start_name", "goal_id", "goal_name",
            "ucs_cost_h", "ucs_nodes_expanded", "astar_cost_h", "astar_nodes_expanded",
            "reduction_pct", "costs_agree",
        ])
        for r in results:
            writer.writerow([
                r.profile_name, r.start, network.nodes[r.start].name, r.goal, network.nodes[r.goal].name,
                r.ucs_cost, r.ucs_nodes_expanded, r.astar_cost, r.astar_nodes_expanded,
                r.reduction_pct, r.costs_agree,
            ])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([s.__dict__ for s in summary], f, indent=2)

    print(f"\n  Raw results written to: {csv_path}")
    print(f"  Summary stats written to: {json_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
