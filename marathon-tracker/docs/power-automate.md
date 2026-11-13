# Power Automate: Shoe Wear Alert

**Business rule:** running shoes wear out (600-700 km). When a new run is logged and the shoe it was run in
has passed 80% of its retirement distance, record an alert so they can buy a replacement in time.

**Flow type:** automated cloud flow, built inside the `Marathon Tracker` solution (so it is exported with the
tables and the app = ALM).

```
Trigger: a row is added to Runs (Dataverse)
  -> Get the shoe used in that run (Shoes)
  -> Sum all km run in that shoe (FetchXML aggregate)
  -> Work out % of retirement distance used
  -> If >= 80%: add a row to the Shoe Alerts table
```

## Column reference (Dataverse logical names)
| Table | Column | Meaning |
|---|---|---|
| Runs `cr28e_runrecord` | `cr28e_shoeidentifier` | shoe number used for the run |
| Runs | `cr28e_distancekilometers` | run distance |
| Shoes `cr28e_shoe` | `cr28e_shoeid1` | shoe number |
| Shoes | `cr28e_modelname` | e.g. Saucony Endorphin Speed 4 |
| Shoes | `cr28e_retirementkilometers` | e.g. 600 |

Test data: shoe 2 (Saucony) is at 543.8 / 600 km = 91%, so any new run with shoe_id 2 should alert.
Shoe 1 is at 24%, so a run with shoe_id 1 should NOT alert (negative test).

## Steps

### 1. Create the flow inside the solution
Solutions > Marathon Tracker > New > Automation > Cloud flow > Automated. Name: `Shoe Wear Alert`.

### 2. Trigger: Dataverse "When a row is added, modified or deleted"
- Change type: **Added**
- Table name: **Runs**
- Scope: **Organization**

### 3. Dataverse "List rows" - rename to `Get shoe`
- Table name: **Shoes**
- Filter rows: `cr28e_shoeid1 eq @{triggerOutputs()?['body/cr28e_shoeidentifier']}`
- Row count: `1`

### 4. Dataverse "List rows" - rename to `Sum shoe km`
- Table name: **Runs**
- Fetch Xml Query:
```xml
<fetch aggregate="true">
  <entity name="cr28e_runrecord">
    <attribute name="cr28e_distancekilometers" alias="totalkm" aggregate="sum" />
    <filter>
      <condition attribute="cr28e_shoeidentifier" operator="eq" value="@{triggerOutputs()?['body/cr28e_shoeidentifier']}" />
    </filter>
  </entity>
</fetch>
```

### 5. Compose actions (Data Operation > Compose)
- `Shoe model`: `first(outputs('Get_shoe')?['body/value'])?['cr28e_modelname']`
- `Retire km`: `first(outputs('Get_shoe')?['body/value'])?['cr28e_retirementkilometers']`
- `Total km`: `first(outputs('Sum_shoe_km')?['body/value'])?['totalkm']`
- `Percent used`: `div(mul(float(outputs('Total_km')), 100), float(outputs('Retire_km')))`

### 6. Condition
`outputs('Percent_used')` **is greater than or equal to** `80`

### 7. If yes: Dataverse "Add a new row"
- Table name: **Shoe Alerts** (`cr28e_shoealert`, created in the same solution)
- Alert: `Time to replace your @{outputs('Shoe_model')}`
- Total km: `@{outputs('Total_km')}`
- Percent used: `@{outputs('Percent_used')}`

If no: do nothing.

Why a table and not an email: the Mail connector is restricted on new tenants and Office 365 Outlook
could not connect on the build day. An alert row has no external dependency, gives a visible history
in the model-driven app, and an email or Teams step can be added after it later.

### 8. Test results (13 Nov 2026)
| Test | Input | Expected | Result |
|---|---|---|---|
| Alert path | New run, shoe_id 2 (Saucony, 600 km life) | Condition true, alert row written | Row: "Time to replace your Saucony Endorphin Speed 4", 553.82 km, 92.30% |
| No-alert path | New run, shoe_id 1 (Nike, 700 km life) | Condition false, nothing written | Condition false, action skipped |

Cross-check: Dataverse sum for shoe 2 = 553.82 km over 57 runs; 553.82 / 600 = 92.3%.

Two bugs found while testing:
- `Retire km` returned empty because of a typo in the column logical name (no error, just null), which made
  `float()` fail in `Percent used`. Fixed by copying the exact logical name.
- "Test with a recently used trigger" replayed the shoe 1 run, so the alert was (correctly) skipped. A real
  shoe 2 run was used instead.

## Design notes (talking points)
- **Why Dataverse trigger, not a schedule:** event-driven = alert arrives right after the run that crosses the line.
- **Why FetchXML aggregate:** Dataverse sums server-side; no loop over every run (fewer API calls, faster, fits
  consumption limits).
- **Known limitation:** after 80% every new run in that shoe alerts again. Improvement: add an
  `alert_sent` yes/no column on Shoes and only notify once.
- **Human oversight:** the flow records an alert; the runner decides. No automatic purchasing.
