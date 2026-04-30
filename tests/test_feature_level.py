def _routes(app):
    return {rule.endpoint for rule in app.url_map.iter_rules()}


def test_v1_has_only_programs_and_health(app_v1):
    routes = _routes(app_v1)
    assert "programs.list_programs" in routes
    assert "health.health" in routes
    assert "clients.list_clients" not in routes
    assert "auth.login" not in routes


def test_v2_adds_clients(app_v2):
    routes = _routes(app_v2)
    assert "clients.list_clients" in routes
    assert "auth.login" not in routes


def test_v3_includes_everything(app_v3):
    routes = _routes(app_v3)
    assert "clients.list_clients" in routes
    assert "auth.login" in routes
    assert "workouts.add_workout" in routes
    assert "workouts.dashboard" in routes
