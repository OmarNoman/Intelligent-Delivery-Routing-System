from fastapi import APIRouter, Depends

from app.api.dependencies import get_network
from app.models.network import RoadNetwork
from app.models.schemas import EdgeOut, NetworkOut, NodeOut

router = APIRouter(tags=["network"])


@router.get("/network", response_model=NetworkOut)
def get_network_data(network: RoadNetwork = Depends(get_network)) -> NetworkOut:
    nodes = [NodeOut(id=n.id, name=n.name, lon=n.lon, lat=n.lat) for n in network.nodes.values()]
    edges = [
        EdgeOut(source=e.source, target=e.target, bumpiness=e.bumpiness, blocked=e.blocked) for e in network.edges
    ]
    return NetworkOut(nodes=nodes, edges=edges)
