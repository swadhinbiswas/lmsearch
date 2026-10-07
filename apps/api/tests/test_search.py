def test_search_returns_hits(client):
    r = client.post("/api/v1/search", json={"query": "Ryzen laptop 32GB RAM", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert "parsed" in data
    assert all("match_score" in h for h in data["hits"])


def test_search_phone_bdt(client):
    r = client.post(
        "/api/v1/search", json={"query": "gaming phone 120Hz 5000mAh below 40k BDT", "limit": 5}
    )
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_product_detail(client):
    r = client.get("/api/v1/products/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_suggest(client):
    r = client.get("/api/v1/suggest", params={"q": "ryz"})
    assert r.status_code == 200
    assert "suggestions" in r.json()


def test_feedback(client):
    r = client.post(
        "/api/v1/feedback", json={"query": "ryzen laptop", "product_id": 1, "event": "click"}
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_admin_reindex_unauthorized(client):
    r = client.post("/api/v1/admin/reindex")
    assert r.status_code == 401
