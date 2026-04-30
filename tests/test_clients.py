def test_create_client(client):
    resp = client.post(
        "/clients/",
        json={"name": "Asha", "age": 30, "weight": 60, "program": "FL"},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Asha"
    assert body["calories"] == 60 * 22


def test_create_client_requires_name(client):
    resp = client.post("/clients/", json={"program": "FL"})
    assert resp.status_code == 400


def test_create_client_validates_program(client):
    resp = client.post("/clients/", json={"name": "X", "program": "ZZ"})
    assert resp.status_code == 400


def test_create_duplicate_returns_409(client):
    p = {"name": "Dup", "weight": 70, "program": "MG"}
    client.post("/clients/", json=p)
    resp = client.post("/clients/", json=p)
    assert resp.status_code == 409


def test_get_client(client):
    client.post(
        "/clients/",
        json={"name": "Meera", "weight": 55, "program": "BG"},
    )
    resp = client.get("/clients/Meera?format=json")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["client"]["name"] == "Meera"
    assert body["client"]["calories"] == 55 * 26


def test_get_unknown_client_404(client):
    assert client.get("/clients/Nope?format=json").status_code == 404


def test_list_clients_json(client):
    client.post("/clients/", json={"name": "A", "weight": 70, "program": "FL"})
    client.post("/clients/", json={"name": "B", "weight": 80, "program": "MG"})
    resp = client.get("/clients/?format=json")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.get_json()["clients"]]
    assert "A" in names and "B" in names


def test_update_client_recomputes_calories(client):
    client.post("/clients/", json={"name": "Ravi", "weight": 70, "program": "FL"})
    resp = client.patch("/clients/Ravi", json={"weight": 80})
    assert resp.status_code == 200
    detail = client.get("/clients/Ravi?format=json").get_json()
    assert detail["client"]["calories"] == 80 * 22


def test_delete_client(client):
    client.post("/clients/", json={"name": "Gone", "weight": 70, "program": "FL"})
    resp = client.delete("/clients/Gone")
    assert resp.status_code == 200
    assert client.get("/clients/Gone?format=json").status_code == 404


def test_add_progress(client):
    client.post("/clients/", json={"name": "Sara", "weight": 60, "program": "BG"})
    resp = client.post(
        "/clients/Sara/progress",
        json={"week": "Week 18 - 2026", "adherence": 85},
    )
    assert resp.status_code == 201


def test_add_progress_validates_range(client):
    client.post("/clients/", json={"name": "Sara2", "weight": 60, "program": "BG"})
    assert client.post("/clients/Sara2/progress", json={"adherence": 200}).status_code == 400
    assert client.post("/clients/Sara2/progress", json={"adherence": -5}).status_code == 400


def test_progress_list(client):
    client.post("/clients/", json={"name": "Tara", "weight": 60, "program": "BG"})
    client.post("/clients/Tara/progress", json={"week": "W1", "adherence": 70})
    client.post("/clients/Tara/progress", json={"week": "W2", "adherence": 85})
    body = client.get("/clients/Tara/progress").get_json()
    assert len(body["progress"]) == 2
