from formatters import format_table, format_today


def test_format_today_empty():
    assert format_today([]) == "Bugun Premier League o'yinlari yo'q."


def test_format_today_converts_to_tashkent_time():
    matches = [
        {
            "utcDate": "2026-10-25T14:00:00Z",
            "homeTeam": {"shortName": "Liverpool"},
            "awayTeam": {"shortName": "Brighton"},
        }
    ]
    result = format_today(matches)
    assert "19:00  Liverpool - Brighton" in result


def test_format_table_row():
    rows = [
        {
            "position": 1,
            "team": {"tla": "MCI"},
            "playedGames": 8,
            "points": 21,
        }
    ]
    result = format_table(rows)
    assert result.startswith("<pre>")
    assert " 1  MCI   8   21" in result

