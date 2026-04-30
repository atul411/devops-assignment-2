def test_add_workout(seeded_client):
    resp = seeded_client.post(
        "/workouts/Ravi",
        json={"workout_type": "Strength", "duration_min": 60, "notes": "Squats"},
    )
    assert resp.status_code == 201


def test_workout_invalid_type(seeded_client):
    resp = seeded_client.post(
        "/workouts/Ravi",
        json={"workout_type": "Yoga", "duration_min": 60},
    )
    assert resp.status_code == 400


def test_workout_unknown_client(seeded_client):
    resp = seeded_client.post(
        "/workouts/Nobody",
        json={"workout_type": "Cardio", "duration_min": 30},
    )
    assert resp.status_code == 404


def test_list_workouts(seeded_client):
    seeded_client.post(
        "/workouts/Ravi",
        json={"workout_type": "Cardio", "duration_min": 45},
    )
    body = seeded_client.get("/workouts/Ravi?format=json").get_json()
    assert body["client"] == "Ravi"
    assert len(body["workouts"]) == 1


def test_add_exercise(seeded_client):
    create = seeded_client.post(
        "/workouts/Ravi",
        json={"workout_type": "Strength", "duration_min": 60},
    )
    workout_id = create.get_json()["id"]
    resp = seeded_client.post(
        f"/workouts/{workout_id}/exercises",
        json={"name": "Squat", "sets": 5, "reps": 5, "weight": 100},
    )
    assert resp.status_code == 201


def test_add_metric(seeded_client):
    resp = seeded_client.post(
        "/metrics/Ravi",
        json={"weight": 75.0, "waist": 85, "bodyfat": 18.5},
    )
    assert resp.status_code == 201


def test_metric_requires_at_least_one_value(seeded_client):
    resp = seeded_client.post("/metrics/Ravi", json={})
    assert resp.status_code == 400


def test_program_generator(seeded_client):
    resp = seeded_client.post("/program-generator/Ravi")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "program" in body
    assert body["client"] == "Ravi"
