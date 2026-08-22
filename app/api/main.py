from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import explain, health, network, routes
from app.config import get_settings
from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.services.routing_service import RoutingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Built once at startup: FuzzySpeedController.__init__ builds a skfuzzy ControlSystem,
    # which is expensive enough that we don't want to redo it on every request.
    settings = get_settings()
    road_network = RoadNetwork.from_json(settings.network_data_path)
    controller = FuzzySpeedController()
    app.state.settings = settings
    app.state.network = road_network
    app.state.controller = controller
    app.state.service = RoutingService(road_network, controller, settings)
    yield


app = FastAPI(
    title="Intelligent Delivery Routing System API",
    description="Route planning, replanning, and fuzzy-speed explainability over the "
    "Melbourne delivery road network.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(network.router)
app.include_router(routes.router)
app.include_router(explain.router)
