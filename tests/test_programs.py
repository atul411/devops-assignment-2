import pytest
from app.models import PROGRAMS, calorie_for, get_program


def test_programs_dict_has_three_known_keys():
    assert set(PROGRAMS.keys()) == {"FL", "MG", "BG"}


def test_each_program_has_required_fields():
    for key, p in PROGRAMS.items():
        for field in ("name", "factor", "color", "workout", "diet"):
            assert field in p, f"{key} missing {field}"


@pytest.mark.parametrize("key,factor", [("FL", 22), ("MG", 35), ("BG", 26)])
def test_calorie_factors_match_v2_source(key, factor):
    assert PROGRAMS[key]["factor"] == factor


@pytest.mark.parametrize(
    "weight,key,expected",
    [
        (70.0, "FL", 1540),
        (80.0, "MG", 2800),
        (60.0, "BG", 1560),
    ],
)
def test_calorie_for_returns_weight_times_factor(weight, key, expected):
    assert calorie_for(weight, key) == expected


def test_calorie_for_rejects_unknown_program():
    with pytest.raises(ValueError):
        calorie_for(70, "XX")


def test_calorie_for_rejects_invalid_weight():
    with pytest.raises(ValueError):
        calorie_for(0, "FL")
    with pytest.raises(ValueError):
        calorie_for(-1, "MG")


def test_get_program_is_case_insensitive():
    assert get_program("fl")["name"] == "Fat Loss"
    assert get_program("Mg")["name"] == "Muscle Gain"


def test_programs_index_redirects_to_programs(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/programs" in resp.headers["Location"]


def test_list_programs_html(client):
    resp = client.get("/programs")
    assert resp.status_code == 200
    assert b"Fat Loss" in resp.data
    assert b"Muscle Gain" in resp.data
    assert b"Beginner" in resp.data


def test_list_programs_json(client):
    resp = client.get("/programs?format=json")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["programs"]) == 3


def test_program_detail_unknown_returns_404(client):
    assert client.get("/programs/XX").status_code == 404


def test_calorie_endpoint(client):
    resp = client.get("/programs/MG/calories?weight=80")
    assert resp.status_code == 200
    assert resp.get_json()["calories"] == 2800


def test_calorie_endpoint_requires_weight(client):
    resp = client.get("/programs/MG/calories")
    assert resp.status_code == 400
