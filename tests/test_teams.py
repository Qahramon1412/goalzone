from teams import find_team

ROWS = [
    {"team": {"name": "Arsenal FC", "shortName": "Arsenal", "tla": "ARS"}},
    {"team": {"name": "Manchester City FC", "shortName": "Man City", "tla": "MCI"}},
]


def test_find_team_by_short_name():
    assert find_team(ROWS, "arsenal") == "Arsenal"


def test_find_team_by_code():
    assert find_team(ROWS, "MCI") == "Man City"


def test_find_team_by_full_name():
    assert find_team(ROWS, "Manchester City FC") == "Man City"


def test_find_team_unknown():
    assert find_team(ROWS, "Barcelona") is None


def test_find_team_empty():
    assert find_team(ROWS, "   ") is None
