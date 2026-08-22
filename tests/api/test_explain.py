import pytest


def test_explain_moderate_rough_matches_worked_example(client):
    resp = client.post("/explain", json={"fragility": 5.0, "bumpiness": 7.0})
    assert resp.status_code == 200
    body = resp.json()

    fired = {r["rule_index"]: r for r in body["fired_rules"]}
    assert set(fired) == {5, 6}
    assert fired[5]["strength"] == pytest.approx(0.3333333333333333)
    assert fired[6]["strength"] == pytest.approx(0.25)
    assert body["crisp_speed"] == pytest.approx(67.1984019054526)


def test_explain_robust_smooth_dominant_not_hardcoded(client):
    # Proves the endpoint isn't just replaying the fragility=5/bumpiness=7 worked example:
    # low inputs should fire only rule 1 (robust & smooth -> fast).
    resp = client.post("/explain", json={"fragility": 0.0, "bumpiness": 0.0})
    assert resp.status_code == 200
    body = resp.json()

    fired = {r["rule_index"]: r for r in body["fired_rules"]}
    assert set(fired) == {1}
    assert fired[1]["fragility_term"] == "robust"
    assert fired[1]["bumpiness_term"] == "smooth"
    assert fired[1]["speed_term"] == "fast"


def test_explain_out_of_range_returns_422(client):
    resp = client.post("/explain", json={"fragility": 11.0, "bumpiness": 5.0})
    assert resp.status_code == 422
