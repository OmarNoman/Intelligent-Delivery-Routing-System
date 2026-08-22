from fastapi import Request

from app.fuzzy.controller import FuzzySpeedController
from app.models.network import RoadNetwork
from app.services.routing_service import RoutingService


def get_network(request: Request) -> RoadNetwork:
    return request.app.state.network


def get_controller(request: Request) -> FuzzySpeedController:
    return request.app.state.controller


def get_service(request: Request) -> RoutingService:
    return request.app.state.service
