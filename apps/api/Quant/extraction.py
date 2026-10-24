import json
from datetime import date


def load_facts(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _days(p: dict) -> int:
    return (date.fromisoformat(p["end"]) - date.fromisoformat(p["start"])).days


def get_flow(facts, concepts, accn, period_end, min_days, max_days):
    """Value for a duration item (revenue, net income...) in one filing."""
    us = facts.get("facts", {}).get("us-gaap", {})
    for concept in concepts:
        points = us.get(concept, {}).get("units", {}).get("USD", [])
        for p in points:
            if (
                p.get("accn") == accn
                and p.get("end") == period_end
                and "start" in p
                and min_days <= _days(p) <= max_days
            ):
                return {
                    "concept": concept,
                    "value": p["val"],
                    "start": p["start"],
                    "end": p["end"],
                    "accn": accn,
                    "form": p.get("form"),
                }
    return None


def get_instant(facts, concepts, accn, period_end):
    """Value for a balance-sheet item on one date, in one filing."""
    us = facts.get("facts", {}).get("us-gaap", {})
    for concept in concepts:
        for p in us.get(concept, {}).get("units", {}).get("USD", []):
            if p.get("accn") == accn and p.get("end") == period_end and "start" not in p:
                return {
                    "concept": concept,
                    "value": p["val"],
                    "end": p["end"],
                    "accn": accn,
                    "form": p.get("form"),
                }
    return None


def get_flow_prior(facts, concepts, accn, period_end, min_days, max_days):
    """Same item for the previous comparable period, from the same filing."""
    us = facts.get("facts", {}).get("us-gaap", {})
    for concept in concepts:
        best = None
        for p in us.get(concept, {}).get("units", {}).get("USD", []):
            if (
                p.get("accn") == accn
                and "start" in p
                and p.get("end", "") < period_end
                and min_days <= _days(p) <= max_days
            ):
                if best is None or p["end"] > best["end"]:
                    best = p
        if best:
            return {
                "concept": concept,
                "value": best["val"],
                "start": best["start"],
                "end": best["end"],
                "accn": accn,
                "form": best.get("form"),
            }
    return None


if __name__ == "__main__":
    try:
        from Quant.compute import REVENUE, COST_OF_REVENUE
    except ModuleNotFoundError:
        from apps.api.Quant.compute import REVENUE, COST_OF_REVENUE

    facts = load_facts("data/facts/0000320193.json")
    accn = "0000320193-23-000106"  # Apple FY 2023 10-K
    period_end = "2023-09-30"

    rev = get_flow(facts, REVENUE, accn, period_end, 350, 380)
    cost = get_flow(facts, COST_OF_REVENUE, accn, period_end, 350, 380)

    print("Revenue:", rev)
    print("Cost of Revenue:", cost)
    if rev and cost:
        gross_margin = (rev["value"] - cost["value"]) / rev["value"]
        print(f"Gross Margin: {gross_margin:.2%}")
