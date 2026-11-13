# Canvas App: Run Logger

Goal: log a new run into the SharePoint **Runs** list, browse recent runs, and see this week's km.
Data source: SharePoint site `https://<your-tenant>.sharepoint.com`, list **Runs**.

> Column names: Power Apps normally shows the list's display names (run_date, run_type, distance_km ...).
> If a name below is not recognised, type `Runs.` in the formula bar and pick the column from the suggestions.

## 1. Create the app
1. https://make.powerapps.com > **Create** > **Blank app** > **Blank canvas app**. Name: `Marathon Run Logger`. Format: **Phone**.
2. Left menu **Data** (cylinder icon) > **Add data** > search `SharePoint` > choose the connection,
   paste the site URL `https://<your-tenant>.sharepoint.com`, tick **Runs** and **Shoes**, and click **Connect**.

If the maker portal asks for a licence or an environment, tell me the message. A SharePoint-only app should
work with the Microsoft 365 licence (standard connector).

## 2. Screens
Rename screens: `scrHome`, `scrLog`.

### scrHome
- Label `lblTitle`: Text = `"Marathon Tracker"`
- Label `lblWeek`: Text =
  ```
  "This week: " & Text(
      Sum(Filter(Runs, run_date >= DateAdd(Today(), -Weekday(Today(), StartOfWeek.Monday) + 1, TimeUnit.Days)), distance_km),
      "0.0") & " km"
  ```
- Gallery `galRuns` (vertical): Items = `SortByColumns(Runs, "run_date", SortOrder.Descending)`
  - Title label: `Text(ThisItem.run_date, "ddd d mmm") & "  " & ThisItem.run_type`
  - Subtitle label: `Text(ThisItem.distance_km, "0.0") & " km  |  " & ThisItem.avg_pace & " /km"`
- Button `btnNew`: Text = `"+ Log run"`, OnSelect = `Navigate(scrLog, ScreenTransition.Cover)`

### scrLog
Controls (names shown):
| Control | Name | Setting |
|---|---|---|
| Date picker | `dpDate` | DefaultDate = `Today()` |
| Dropdown | `ddType` | Items = `["Easy","Tempo","Intervals","Long","Race"]` |
| Text input | `txtKm` | Format = Number, HintText = `"Distance (km)"` |
| Text input | `txtMin` | Format = Number, HintText = `"Duration (min)"` |
| Text input | `txtHR` | Format = Number, HintText = `"Avg heart rate"` |
| Dropdown | `ddShoe` | Items = `Shoes`, Value = `model` |
| Slider | `sldRPE` | Min 1, Max 10, Default 5 |
| Label | `lblPace` | Text = see below |
| Button | `btnSave` | see below |

Pace preview, `lblPace.Text`:
```
If(Value(txtKm.Text) > 0 And Value(txtMin.Text) > 0,
   Text(RoundDown(Value(txtMin.Text) / Value(txtKm.Text), 0), "0") & ":" &
   Text(Round(Mod(Value(txtMin.Text) / Value(txtKm.Text), 1) * 60, 0), "00") & " /km",
   "")
```

`btnSave.DisplayMode` (disable until valid):
```
If(Value(txtKm.Text) > 0 And Value(txtMin.Text) > 0, DisplayMode.Edit, DisplayMode.Disabled)
```

`btnSave.OnSelect`:
```
Patch(Runs, Defaults(Runs), {
    Title: Text(Max(Runs, Value(Title)) + 1),       // run_id
    run_date: dpDate.SelectedDate,
    run_type: ddType.Selected.Value,
    distance_km: Value(txtKm.Text),
    duration_min: Value(txtMin.Text),
    avg_pace: lblPace.Text,
    avg_hr: Value(txtHR.Text),
    shoe_id: ddShoe.Selected.shoe_id,
    rpe: sldRPE.Value
});
If(IsEmpty(Errors(Runs)),
   Notify("Run saved", NotificationType.Success); Navigate(scrHome, ScreenTransition.UncoverRight),
   Notify("Could not save: " & First(Errors(Runs)).Message, NotificationType.Error))
```
> `Title` is the run_id column (stored as text). If `Max(Runs, Value(Title))` is flagged as a delegation
> warning, that is fine for 120 rows. Note it in the README as a known limit.

## 3. Test
1. Press F5 (play), tap **+ Log run**, enter 8 km, 45 min, HR 150, tap **Save**.
2. Open the Runs list in SharePoint: a new row (run_id 120) should be at the bottom.
3. Refresh the Power BI report: Total KM should rise by 8.

## 4. Publish and export (ALM evidence)
1. **Save** then **Publish** in Power Apps Studio.
2. Make portal > **Apps** > your app > **Export package (.zip)** > save into `powerplatform/solution/`.
3. Screenshot both screens into `docs/screenshots/`.
