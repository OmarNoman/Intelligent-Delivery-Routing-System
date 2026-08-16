import json
from dataclasses import dataclass
from pathlib import Path

import haversine as hav
from haversine import Unit


@dataclass(frozen=True)
class Node:
    id: int
    name: str
    lon: float
    lat: float


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    bumpiness: float
    blocked: bool


class RoadNetwork:
    # Melbourne suburb road network for cargo delivery planning.
    # Handles graph generation, blocked-edge constraints, Haversine distances, and road bumpiness.

    def __init__(self, nodes: dict[int, Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges
        self.blocked_pairs = self._build_blocked_pairs()
        self.graph = self._build_graph()
        self.bumpiness_map = self._build_bumpiness_map()

    @classmethod
    def from_json(cls, path: str | Path) -> "RoadNetwork":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        nodes = {
            n["id"]: Node(id=n["id"], name=n["name"], lon=n["lon"], lat=n["lat"])
            for n in data["nodes"]
        }
        edges = [
            Edge(source=e["source"], target=e["target"], bumpiness=e["bumpiness"], blocked=e["blocked"])
            for e in data["edges"]
        ]
        return cls(nodes, edges)

    def haversine_km(self, node1: int, node2: int) -> float:
        # Geodesic distance in km between two node ids (Haversine)
        lon1, lat1 = self.nodes[node1].lon, self.nodes[node1].lat
        lon2, lat2 = self.nodes[node2].lon, self.nodes[node2].lat
        return round(hav.haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS), 4)

    def _build_blocked_pairs(self) -> set[tuple[int, int]]:
        pairs = set()
        for e in self.edges:
            if e.blocked:
                pairs.add((e.source, e.target))
                pairs.add((e.target, e.source))
        return pairs

    def _build_graph(self) -> dict:
        # Builds the undirected weighted adjacency list from self.edges
        graph = {n: [] for n in self.nodes}
        for e in self.edges:
            d = self.haversine_km(e.source, e.target)
            graph[e.source].append((e.target, d))
            graph[e.target].append((e.source, d))
        return graph

    def _build_bumpiness_map(self) -> dict:
        return {frozenset({e.source, e.target}): e.bumpiness for e in self.edges}

    def get_neighbors(self, node: int) -> list:
        # Returns the (neighbour, distance_km) excluding blocked edges
        return [
            (nb, d) for nb, d in self.graph[node]
            if (node, nb) not in self.blocked_pairs
        ]

    def get_all_edges(self) -> list:
        # Return all 36 unique edges as a sorted list of frozensets
        edges = {frozenset({e.source, e.target}) for e in self.edges}
        return sorted(edges, key=lambda e: sorted(e))

    def get_bumpiness(self, edge: frozenset) -> float:
        return self.bumpiness_map.get(edge, 5.0)
