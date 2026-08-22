from fastapi import APIRouter, Depends

from app.api.dependencies import get_network
from app.models.network import RoadNetwork
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(network: RoadNetwork = Depends(get_network)) -> HealthResponse:
    return HealthResponse(status="ok", node_count=len(network.nodes), edge_count=len(network.get_all_edges()))
