def find_team(rows, query):
    """Jadval qatorlaridan jamoani topadi. Topilsa shortName, aks holda None."""
    q = query.strip().lower()
    if not q:
        return None
    for r in rows:
        t = r["team"]
        names = {t["name"].lower(), t["shortName"].lower(), t["tla"].lower()}
        if q in names:
            return t["shortName"]
    return None


def filter_matches(matches, team):
    """Faqat berilgan jamoa qatnashgan o'yinlarni qaytaradi."""
    return [
        m
        for m in matches
        if team in (m["homeTeam"]["shortName"], m["awayTeam"]["shortName"])
    ]
