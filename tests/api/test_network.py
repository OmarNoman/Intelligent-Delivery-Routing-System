def test_network_shape(client):
    resp = client.get("/network")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["nodes"]) == 21
    assert len(body["edges"]) == 36

    node = next(n for n in body["nodes"] if n["id"] == 0)
    assert node["name"] == "Melbourne CBD"

    assert all({"source", "target", "bumpiness", "blocked"} <= e.keys() for e in body["edges"])
