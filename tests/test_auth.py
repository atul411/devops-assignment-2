def test_login_success(client):
    resp = client.post(
        "/login",
        json={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["role"] == "Admin"


def test_login_wrong_password(client):
    resp = client.post(
        "/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/login",
        json={"username": "ghost", "password": "x"},
    )
    assert resp.status_code == 401


def test_logout_clears_session(auth_client):
    me = auth_client.get("/me")
    assert me.status_code == 200
    auth_client.get("/logout")
    me_after = auth_client.get("/me")
    assert me_after.status_code == 401


def test_protected_endpoint_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code in (302, 401)
