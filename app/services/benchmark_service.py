import math
import statistics
from dataclasses import dataclass

from app.config import Settings
from app.models.network import RoadNetwork
from app.routing.search import astar_time, ucs_time
from app.services.routing_service import RoutingService


@dataclass(frozen=True)
class SpeedProfile:
    name: str
    segment_speeds: dict
    max_speed_ref: float


@dataclass(frozen=True)
class BenchmarkResult:
    profile_name: str
    start: int
    goal: int
    ucs_cost: float
    ucs_nodes_expanded: int
    astar_cost: float
    astar_nodes_expanded: int
    reduction_pct: float
    costs_agree: bool


@dataclass(frozen=True)
class SummaryStats:
    label: str
    n: int
    mean: float
    median: float
    stdev: float
    minimum: float
    maximum: float
    ci95_low: float
    ci95_high: float


def default_profiles(network: RoadNetwork, service: RoutingService, settings: Settings) -> list:
    profiles = [
        SpeedProfile(
            name="flat_100kmh",
            segment_speeds={e: settings.baseline_speed for e in network.get_all_edges()},
            max_speed_ref=settings.baseline_speed,
        )
    ]
    for fragility in settings.fragility_levels:
        speeds = service.compute_segment_speeds(fragility)
        profiles.append(
            SpeedProfile(
                name=f"fis_fragility_{fragility}",
                segment_speeds=speeds,
                max_speed_ref=max(speeds.values()),
            )
        )
    return profiles


def run_full_sweep(network: RoadNetwork, profiles: list, baseline_speed: float) -> list:
    node_ids = sorted(network.nodes.keys())
    results = []
    for profile in profiles:
        for start in node_ids:
            for goal in node_ids:
                if start == goal:
                    continue
                _, ucs_cost, ucs_exp = ucs_time(network, start, goal, profile.segment_speeds, baseline_speed)
                _, ast_cost, ast_exp = astar_time(
                    network, start, goal, profile.segment_speeds, profile.max_speed_ref, baseline_speed
                )
                reduction_pct = (ucs_exp - ast_exp) / ucs_exp * 100 if ucs_exp > 0 else 0.0
                costs_agree = math.isclose(ucs_cost, ast_cost, rel_tol=1e-9, abs_tol=1e-9)
                results.append(
                    BenchmarkResult(
                        profile_name=profile.name,
                        start=start,
                        goal=goal,
                        ucs_cost=ucs_cost,
                        ucs_nodes_expanded=ucs_exp,
                        astar_cost=ast_cost,
                        astar_nodes_expanded=ast_exp,
                        reduction_pct=reduction_pct,
                        costs_agree=costs_agree,
                    )
                )
    return results


def _summarize_values(label: str, values: list) -> SummaryStats:
    n = len(values)
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if n >= 2 else 0.0
    ci_half_width = 1.96 * stdev / math.sqrt(n) if n >= 2 else 0.0
    return SummaryStats(
        label=label,
        n=n,
        mean=mean,
        median=statistics.median(values),
        stdev=stdev,
        minimum=min(values),
        maximum=max(values),
        ci95_low=mean - ci_half_width,
        ci95_high=mean + ci_half_width,
    )


def summarize(results: list) -> list:
    by_profile: dict = {}
    for r in results:
        by_profile.setdefault(r.profile_name, []).append(r.reduction_pct)

    summaries = [_summarize_values(name, values) for name, values in by_profile.items()]
    if results:
        summaries.append(_summarize_values("combined", [r.reduction_pct for r in results]))
    return summaries
