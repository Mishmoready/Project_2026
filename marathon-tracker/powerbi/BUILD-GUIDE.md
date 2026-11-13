# Power BI build guide

Data comes from the SharePoint lists Runs, Races and Shoes (site `https://<your-tenant>.sharepoint.com`),
plus the Recovery CSV. Files here: [queries.pq](queries.pq) and [measures.dax](measures.dax).

## 1. Load the data (about 10 minutes)
1. Power BI Desktop > Home > **Transform data** > New Source > **Blank Query**.
2. Open **Advanced Editor**, paste the **Runs** query from queries.pq, and click Done.
3. First time only: sign in with the work account (`<you>@<your-tenant>.onmicrosoft.com`), choose
   **Organizational account**, and click Connect.
4. Rename the query to `Runs`. Repeat for `Races`, `Shoes`, `RaceSplits` (after Races) and `Recovery`.
5. **Close & Apply**.
6. If a query says a column is missing, open the step that fails and tell me the column names it shows.

## 2. Model
1. Modeling > New table: paste the `Date` table from measures.dax. Right-click it > **Mark as date table** on `Date`.
2. Relationships (all many-to-one, single direction):
   - Runs[run_day] -> Date[Date]
   - Races[race_day] -> Date[Date]
   - Recovery[date] -> Date[Date]
   - Runs[shoe_id] -> Shoes[shoe_id]
   - RaceSplits[race_id] -> Races[race_id]
3. Add the measures from measures.dax (New measure, one at a time).

## 3. Report pages (dark theme: View > Themes)
| Page | Visuals |
|---|---|
| Overview | Cards: Total KM, Run Count, Longest Run KM, ACWR. Column chart: Weekly KM by Date[Week Start]. Slicer: Date[Month] |
| Training | Line: Avg HR and pace by month. Bar: Total KM by run_type. Scatter: distance vs duration |
| Races | Table: race_name, Race Finish, Goal vs Finish. Line: RaceSplits split_sec by km_mark per race |
| Recovery | Line charts: Avg Sleep, Avg HRV, Avg Resting HR, weight by Date |
| Gear | Bar: Shoe Life Used % by Shoes[model], with a 100% reference line |

## 4. Save
Save as `powerbi/marathon-tracker.pbip` (File > Save as > Power BI Project) so it is diff-friendly in Git.
Take screenshots of each page into `docs/screenshots/` for the README.
