# Data model

Star schema. Facts at the run/race/day grain, dimensions for date, shoes and plan weeks.

| Table | Grain | Key columns |
|---|---|---|
| dim_date | day | date |
| dim_shoes | shoe | shoe_id, retire_km |
| dim_plan | training week | week_no, week_start, phase, planned_km |
| fact_runs | run | run_id, run_date, shoe_id, distance_km, duration_min, avg_hr, rpe |
| fact_races | race | race_id, race_date, distance_km, goal/finish_time_sec, split_5k..40k |
| fact_recovery | day | date, weight_kg, resting_hr, sleep_hours, hrv_ms, soreness |

## Relationships (all many-to-one, single direction)
- fact_runs[run_date] -> dim_date[date]
- fact_recovery[date] -> dim_date[date]
- fact_races[race_date] -> dim_date[date]
- fact_runs[shoe_id] -> dim_shoes[shoe_id]
- dim_plan[week_start] -> dim_date[date]

## Starter DAX measures
```dax
Total KM = SUM ( fact_runs[distance_km] )
Weekly KM = CALCULATE ( [Total KM], ALLEXCEPT ( dim_date, dim_date[week_no] ) )
Planned KM = SUM ( dim_plan[planned_km] )
Plan Adherence % = DIVIDE ( [Total KM], [Planned KM] )
Avg HR = AVERAGE ( fact_runs[avg_hr] )
Shoe KM = CALCULATE ( [Total KM], ALLEXCEPT ( dim_shoes, dim_shoes[shoe_id] ) )
Shoe Life Used % = DIVIDE ( [Shoe KM], MAX ( dim_shoes[retire_km] ) )
Acute Load (7d) = CALCULATE ( [Total KM], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -7, DAY ) )
Chronic Load (28d) = CALCULATE ( [Total KM], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -28, DAY ) ) / 4
ACWR = DIVIDE ( [Acute Load (7d)], [Chronic Load (28d)] )
```
Mark dim_date as the date table. ACWR above 1.5 is a common "injury risk" flag.

## Report pages
1. Overview: weekly km vs plan, streak, PRs, ACWR card
2. Training: pace and HR trend by run type, long-run progression
3. Races: goal vs finish, 5K splits (pacing)
4. Recovery: sleep, HRV, resting HR, weight trend
5. Gear: shoe mileage vs retirement
