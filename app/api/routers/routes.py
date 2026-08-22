from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_network, get_service
from app.models.network import RoadNetwork
from app.models.schemas import RerouteRequest, RerouteResponse, RoutePlanRequest, RoutePlanResponse
from app.services.routing_service import RoutingService

router = APIRouter(prefix="/routes", tags=["routes"])


def _require_known_nodes(network: RoadNetwork, *node_ids: int) -> None:
    for node_id in node_ids:
        if node_id not in network.nodes:
            raise HTTPException(status_code=404, detail=f"Unknown node id: {node_id}")


def _path_names(network: RoadNetwork, path: list) -> list[str]:
    return [network.nodes[n].name for n in path]


@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(
    req: RoutePlanRequest,
    network: RoadNetwork = Depends(get_network),
    service: RoutingService = Depends(get_service),
) -> RoutePlanResponse:
    _require_known_nodes(network, req.start, req.goal)

    if req.fragility is None:
        segment_speeds = {frozenset(e): service.settings.baseline_speed for e in network.get_all_edges()}
    else:
        segment_speeds = service.compute_segment_speeds(req.fragility)

    if req.constrained:
        constrained_edges = service.sample_constrained_edges()
        segment_speeds = service.apply_constraints(segment_speeds, constrained_edges)

    if req.algorithm == "astar":
        path, cost, nodes_expanded = service.astar_time(
            req.start, req.goal, segment_speeds, max(segment_speeds.values())
        )
    else:
        path, cost, nodes_expanded = service.ucs_time(req.start, req.goal, segment_speeds)

    if path is None:
        raise HTTPException(status_code=400, detail=f"No path found between {req.start} and {req.goal}")

    return RoutePlanResponse(
        path=path,
        path_names=_path_names(network, path),
        algorithm=req.algorithm,
        cost_h=cost,
        cost_min=cost * 60,
        nodes_expanded=nodes_expanded,
        distance_km=service.path_distance_km(path),
    )


@router.post("/reroute", response_model=RerouteResponse)
def reroute(
    req: RerouteRequest,
    network: RoadNetwork = Depends(get_network),
    service: RoutingService = Depends(get_service),
) -> RerouteResponse:
    _require_known_nodes(network, req.start, req.goal)

    initial_speeds = service.compute_segment_speeds(req.fragility)
    constrained_edges = service.sample_constrained_edges(fraction=req.constraint_fraction)
    constrained_speeds = service.apply_constraints(initial_speeds, constrained_edges)

    result = service.simulate_replanning(req.start, req.goal, initial_speeds, constrained_speeds)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return RerouteResponse(
        init_path=result["init_path"],
        init_path_names=_path_names(network, result["init_path"]),
        replan_path=result["replan_path"],
        replan_path_names=_path_names(network, result["replan_path"]),
        full_path=result["full_path"],
        full_path_names=_path_names(network, result["full_path"]),
        trigger_node=result["trigger_node"],
        trigger_node_name=network.nodes[result["trigger_node"]].name,
        trigger_idx=result["trigger_idx"],
        total_time_h=result["total_time_h"],
        total_time_min=result["total_time_h"] * 60,
        nodes_expanded=result["nodes_exp"],
        constrained_edge_count=len(constrained_edges),
    )
