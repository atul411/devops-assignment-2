def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert "version" in body
    assert body["feature_level"] == 3


def test_ready_returns_ok_when_db_up(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_health_at_each_feature_level(client_v1, client_v2, client):
    assert client_v1.get("/health").get_json()["feature_level"] == 1
    assert client_v2.get("/health").get_json()["feature_level"] == 2
    assert client.get("/health").get_json()["feature_level"] == 3
