"""Trip planner agent: retrieves, ranks, schedules and budgets an itinerary."""
from .rag import KnowledgeBase
from . import weather

DAY_HOURS = 7.0       # sightseeing hours per day
TRAVEL_BUFFER = 0.5   # hours lost per stop to travel
TIERS = [("budget", 1500, 1200), ("standard", 4000, 3000), ("comfort", 10**9, 7000)]
# (name, max per-person-per-day budget, estimated stay+food+local transport per person per day, INR)


def pick_tier(total_budget, days, travelers):
    per_day = total_budget / max(days * travelers, 1)
    for name, limit, base in TIERS:
        if per_day <= limit:
            return name, base
    return TIERS[-1][0], TIERS[-1][2]


def plan_trip(kb: KnowledgeBase, destination, days, budget, travelers=1, interests=None, use_weather=True):
    if destination not in kb.data:
        raise ValueError(f"Unknown destination: {destination}")
    interests = interests or []
    query = " ".join(interests) or "popular sights"
    ranked = kb.search(query, dest=destination, kind="attraction", k=50)
    scored = []
    for score, doc in ranked:
        a = doc["item"]
        bonus = 0.5 if a["category"] in [i.lower() for i in interests] else 0
        scored.append((score + bonus, a))
    scored.sort(key=lambda x: -x[0])

    # Greedy selection into the available hours, then group by area to cut travel.
    capacity = days * DAY_HOURS
    chosen, used = [], 0.0
    for _, a in scored:
        need = a["hours"] + TRAVEL_BUFFER
        if used + need <= capacity:
            chosen.append(a)
            used += need
    chosen.sort(key=lambda a: (a["area"], -a["hours"]))

    plan = [{"day": i + 1, "stops": [], "hours": 0.0} for i in range(days)]
    for a in chosen:
        day = min(plan, key=lambda d: d["hours"])
        # prefer a day that already visits this area
        same = [d for d in plan if any(s["area"] == a["area"] for s in d["stops"])
                and d["hours"] + a["hours"] + TRAVEL_BUFFER <= DAY_HOURS]
        day = same[0] if same else day
        day["stops"].append(a)
        day["hours"] += a["hours"] + TRAVEL_BUFFER

    tier, base = pick_tier(budget, days, travelers)
    entry = sum(a["cost"] for a in chosen) * travelers
    living = base * days * travelers
    total = entry + living
    result = {
        "destination": destination, "days": days, "travelers": travelers, "tier": tier,
        "best_months": kb.data[destination]["best_months"],
        "itinerary": [{"day": d["day"], "hours": round(d["hours"], 1),
                       "stops": [{k: s[k] for k in ("name", "category", "area", "hours", "cost", "desc")}
                                 for s in d["stops"]]} for d in plan],
        "budget": {"entry_fees": entry, "stay_food_transport": living, "estimated_total": total,
                   "your_budget": budget, "within_budget": total <= budget,
                   "difference": budget - total},
        "tips": [d["item"] for _, d in kb.search("tips", dest=destination, kind="tip", k=3)],
        "weather": [],
    }
    if use_weather:
        info = kb.data[destination]
        result["weather"] = weather.forecast(info["lat"], info["lon"], min(days, 7))
    return result
