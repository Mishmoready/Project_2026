"""Generate reproducible fake marathon-training data (stdlib only).

Usage: python scripts/generate_data.py [--seed 42] [--out data/generated]
Outputs: dim_date, dim_shoes, dim_plan, fact_runs, fact_races, fact_recovery
"""
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

START = date(2026, 1, 5)          # a Monday
WEEKS = 26
MARATHON_WEEK = 24                # 0-indexed week of the goal marathon
GOAL_MARATHON = date(2026, 6, 21)


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fmt_pace(sec_per_km):
    return f"{int(sec_per_km // 60)}:{int(sec_per_km % 60):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/generated")
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    shoes = [
        {"shoe_id": 1, "model": "Nike Pegasus 41", "purchase_date": "2025-12-01", "retire_km": 700},
        {"shoe_id": 2, "model": "Saucony Endorphin Speed 4", "purchase_date": "2026-02-15", "retire_km": 600},
        {"shoe_id": 3, "model": "Asics Novablast 5", "purchase_date": "2026-04-10", "retire_km": 700},
    ]

    # Periodised weekly km: build 3 weeks, cutback 1, taper last 3 weeks
    plan, peak = [], 75
    for w in range(WEEKS):
        if w >= MARATHON_WEEK + 1:
            km, phase = 0, "Recovery"
        elif w >= MARATHON_WEEK - 2:
            km, phase = peak * (0.7 if w == MARATHON_WEEK - 2 else 0.5 if w == MARATHON_WEEK - 1 else 0.3), "Taper"
        else:
            base = 30 + (peak - 30) * w / (MARATHON_WEEK - 3)
            km = base * (0.75 if w % 4 == 3 else 1)
            phase = "Base" if w < 8 else "Build" if w < 18 else "Peak"
        plan.append({"week_no": w + 1, "week_start": (START + timedelta(weeks=w)).isoformat(),
                     "phase": phase, "planned_km": round(km, 1)})

    runs, rid = [], 1
    for p in plan:
        w = p["week_no"] - 1
        if p["planned_km"] == 0:
            continue
        injured = w in (13, 14) and rnd.random() < 0.8          # a rough patch
        skip_prob = 0.6 if injured else 0.08
        long_km = min(p["planned_km"] * 0.35, 32)
        rest = p["planned_km"] - long_km
        layout = [(1, "Easy", rest * 0.2), (2, "Tempo" if p["phase"] != "Taper" else "Easy", rest * 0.25),
                  (3, "Easy", rest * 0.2), (4, "Intervals" if p["phase"] in ("Build", "Peak") else "Easy", rest * 0.2),
                  (6, "Long", long_km)]
        for dow, rtype, km in layout:
            if rnd.random() < skip_prob:
                continue
            d = START + timedelta(weeks=w, days=dow)
            if d >= GOAL_MARATHON and d <= GOAL_MARATHON + timedelta(days=1) or d > GOAL_MARATHON + timedelta(days=60):
                continue
            km = max(4, km * rnd.uniform(0.92, 1.08))
            fitness = 1 - 0.12 * (w / MARATHON_WEEK)               # gets faster over time
            base = {"Easy": 360, "Long": 345, "Tempo": 310, "Intervals": 295}[rtype] * fitness
            pace = base * rnd.uniform(0.97, 1.04)
            hr = {"Easy": 140, "Long": 148, "Tempo": 165, "Intervals": 172}[rtype] + rnd.randint(-5, 5) - int(w / 4)
            shoe = 1 if d < date(2026, 2, 15) else 2 if d < date(2026, 4, 10) or rtype in ("Tempo", "Intervals") else 3
            runs.append({
                "run_id": rid, "run_date": d.isoformat(), "run_type": rtype,
                "distance_km": round(km, 2), "duration_min": round(km * pace / 60, 1),
                "avg_pace": fmt_pace(pace), "avg_hr": hr, "max_hr": hr + rnd.randint(10, 22),
                "elevation_m": rnd.randint(10, 220), "shoe_id": shoe,
                "weather": rnd.choice(["Clear", "Cloudy", "Rain", "Windy", "Hot"]),
                "temp_c": rnd.randint(2, 28), "rpe": min(10, max(2, {"Easy": 3, "Long": 6, "Tempo": 7, "Intervals": 8}[rtype] + rnd.randint(-1, 2))),
            })
            rid += 1

    # Races: tune-ups + goal marathon (with 5K splits)
    race_defs = [("Winter 10K", date(2026, 2, 8), 10, 3000), ("Spring Half Marathon", date(2026, 4, 5), 21.0975, 6300),
                 ("Tune-up 15K", date(2026, 5, 10), 15, 4600), ("City Marathon", GOAL_MARATHON, 42.195, 13800)]
    races = []
    for i, (name, d, dist, goal) in enumerate(race_defs, 1):
        finish = int(goal * rnd.uniform(0.97, 1.06))
        row = {"race_id": i, "race_name": name, "race_date": d.isoformat(), "distance_km": dist,
               "goal_time_sec": goal, "finish_time_sec": finish,
               "overall_position": rnd.randint(200, 2500), "location": rnd.choice(["London", "Manchester", "Edinburgh", "Bristol"])}
        pace = finish / dist
        for k in range(1, 9):
            row[f"split_{k*5}k"] = round(pace * 5 * (1 + (0.002 * k if dist > 21 else 0)) * rnd.uniform(0.98, 1.03)) if k * 5 <= dist else ""
        races.append(row)
        runs.append({"run_id": rid, "run_date": d.isoformat(), "run_type": "Race", "distance_km": round(dist, 2),
                     "duration_min": round(finish / 60, 1), "avg_pace": fmt_pace(pace), "avg_hr": 170, "max_hr": 186,
                     "elevation_m": rnd.randint(20, 150), "shoe_id": 2, "weather": "Clear", "temp_c": 12, "rpe": 9})
        rid += 1
    runs.sort(key=lambda r: r["run_date"])

    # Daily recovery metrics
    rec, wt = [], 78.0
    last = START + timedelta(weeks=WEEKS)
    d = START
    while d < last:
        wt += rnd.uniform(-0.15, 0.1) - 0.004
        rec.append({"date": d.isoformat(), "weight_kg": round(wt, 1),
                    "resting_hr": round(58 - 6 * (d - START).days / 180 + rnd.uniform(-2, 2)),
                    "sleep_hours": round(min(9.5, max(4.5, rnd.gauss(7.2, 0.8))), 1),
                    "hrv_ms": round(max(25, rnd.gauss(62, 9))), "soreness": rnd.randint(1, 5)})
        d += timedelta(days=1)

    # Date dimension
    dates, d = [], START
    while d < last:
        dates.append({"date": d.isoformat(), "year": d.year, "month_no": d.month, "month": d.strftime("%b"),
                      "week_no": (d - START).days // 7 + 1, "day_of_week": d.strftime("%a"),
                      "dow_no": d.isoweekday(), "is_weekend": int(d.weekday() >= 5)})
        d += timedelta(days=1)

    write(out / "dim_date.csv", dates, list(dates[0]))
    write(out / "dim_shoes.csv", shoes, list(shoes[0]))
    write(out / "dim_plan.csv", plan, list(plan[0]))
    write(out / "fact_runs.csv", runs, list(runs[0]))
    write(out / "fact_races.csv", races, list(races[0]))
    write(out / "fact_recovery.csv", rec, list(rec[0]))
    print(f"Wrote {len(runs)} runs, {len(races)} races, {len(rec)} recovery days to {out}")


if __name__ == "__main__":
    main()
