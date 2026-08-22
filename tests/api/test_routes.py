import pytest

BASELINE_PATH = [20, 4, 18, 9, 0, 14, 13, 17]


def test_plan_baseline_matches_golden_path(client):
    resp = client.post("/routes/plan", json={"start": 20, "goal": 17})
    assert resp.status_code == 200
    body = resp.json()
    assert body["path"] == BASELINE_PATH
    assert body["algorithm"] == "astar"
    assert body["cost_h"] == pytest.approx(0.601077, abs=1e-5)
    assert body["nodes_expanded"] == 12
    assert body["path_names"][0] == "Hoppers Crossing"
    assert body["path_names"][-1] == "Ferntree Gully"
    assert body["distance_km"] > 0


def test_plan_ucs_agrees_on_cost_with_astar(client):
    astar_resp = client.post("/routes/plan", json={"start": 20, "goal": 17, "algorithm": "astar"})
    ucs_resp = client.post("/routes/plan", json={"start": 20, "goal": 17, "algorithm": "ucs"})
    assert astar_resp.json()["cost_h"] == pytest.approx(ucs_resp.json()["cost_h"])
    # A* should never expand more nodes than UCS on an admissible heuristic
    assert astar_resp.json()["nodes_expanded"] <= ucs_resp.json()["nodes_expanded"]


def test_plan_with_fuzzy_fragility_matches_pinned_service_value(client):
    resp = client.post("/routes/plan", json={"start": 20, "goal": 17, "fragility": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["path"] == BASELINE_PATH
    assert body["cost_h"] == pytest.approx(0.8396122885331007)
    assert body["nodes_expanded"] == 15


def test_plan_constrained_caps_speeds_and_changes_cost(client):
    unconstrained = client.post("/routes/plan", json={"start": 20, "goal": 17, "fragility": 5})
    constrained = client.post("/routes/plan", json={"start": 20, "goal": 17, "fragility": 5, "constrained": True})
    assert constrained.status_code == 200
    # Capping edge speeds can only ever keep travel time the same or make it worse
    assert constrained.json()["cost_h"] >= unconstrained.json()["cost_h"]


def test_plan_unknown_node_returns_404(client):
    resp = client.post("/routes/plan", json={"start": 999, "goal": 17})
    assert resp.status_code == 404


def test_plan_fragility_out_of_range_returns_422(client):
    resp = client.post("/routes/plan", json={"start": 20, "goal": 17, "fragility": 15})
    assert resp.status_code == 422
