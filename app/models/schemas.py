from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    node_count: int
    edge_count: int


class NodeOut(BaseModel):
    id: int
    name: str
    lon: float
    lat: float


class EdgeOut(BaseModel):
    source: int
    target: int
    bumpiness: float
    blocked: bool


class NetworkOut(BaseModel):
    nodes: list[NodeOut]
    edges: list[EdgeOut]


class RoutePlanRequest(BaseModel):
    start: int
    goal: int
    fragility: float | None = Field(default=None, ge=0, le=10)
    algorithm: Literal["astar", "ucs"] = "astar"
    constrained: bool = False


class RoutePlanResponse(BaseModel):
    path: list[int]
    path_names: list[str]
    algorithm: Literal["astar", "ucs"]
    cost_h: float
    cost_min: float
    nodes_expanded: int
    distance_km: float


class RerouteRequest(BaseModel):
    start: int
    goal: int
    fragility: float = Field(ge=0, le=10)
    constraint_fraction: float | None = Field(default=None, ge=0, le=1)


class RerouteResponse(BaseModel):
    init_path: list[int]
    init_path_names: list[str]
    replan_path: list[int]
    replan_path_names: list[str]
    full_path: list[int]
    full_path_names: list[str]
    trigger_node: int
    trigger_node_name: str
    trigger_idx: int
    total_time_h: float
    total_time_min: float
    nodes_expanded: int
    constrained_edge_count: int


class ExplainRequest(BaseModel):
    fragility: float = Field(ge=0, le=10)
    bumpiness: float = Field(ge=0, le=10)


class FiredRuleOut(BaseModel):
    rule_index: int
    fragility_term: str
    bumpiness_term: str
    speed_term: str
    strength: float


class ExplainResponse(BaseModel):
    fragility: float
    bumpiness: float
    fragility_memberships: dict[str, float]
    bumpiness_memberships: dict[str, float]
    fired_rules: list[FiredRuleOut]
    crisp_speed: float
