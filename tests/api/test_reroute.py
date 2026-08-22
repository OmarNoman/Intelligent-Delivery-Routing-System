def test_reroute_shape_and_sanity(client):
    resp = client.post("/routes/reroute", json={"start": 20, "goal": 17, "fragility": 5})
    assert resp.status_code == 200
    body = resp.json()

    assert body["init_path"][0] == 20
    assert body["init_path"][-1] == 17
    assert body["full_path"][0] == 20
    assert body["full_path"][-1] == 17
    assert body["replan_path"][0] == body["trigger_node"]
    assert body["replan_path"][-1] == 17
    assert 0 <= body["trigger_idx"] < len(body["init_path"]) - 1
    assert body["trigger_node_name"]
    assert body["total_time_h"] > 0
    assert body["total_time_min"] == body["total_time_h"] * 60
    assert body["nodes_expanded"] > 0
    assert body["constrained_edge_count"] == round(0.60 * 36)  # default constraint_fraction


def test_reroute_custom_constraint_fraction_changes_edge_count(client):
    resp = client.post(
        "/routes/reroute", json={"start": 20, "goal": 17, "fragility": 5, "constraint_fraction": 0.2}
    )
    assert resp.status_code == 200
    assert resp.json()["constrained_edge_count"] == round(0.2 * 36)


def test_reroute_unknown_node_returns_404(client):
    resp = client.post("/routes/reroute", json={"start": 999, "goal": 17, "fragility": 5})
    assert resp.status_code == 404


def test_reroute_missing_fragility_returns_422(client):
    resp = client.post("/routes/reroute", json={"start": 20, "goal": 17})
    assert resp.status_code == 422
