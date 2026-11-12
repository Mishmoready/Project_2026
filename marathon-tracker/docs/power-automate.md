# Power Automate: Shoe Wear Alert

**Business rule:** running shoes wear out (600-700 km). When a new run is logged and the shoe it was run in
has passed 80% of its retirement distance, notify the runner so they can buy a replacement in time.

**Flow type:** automated cloud flow, built inside the `Marathon Tracker` solution (so it is exported with the
tables and the app = ALM).

```
Trigger: a row is added to Runs (Dataverse)
  -> Get the shoe used in that run (Shoes)
  -> Sum all km run in that shoe (FetchXML aggregate)
  -> Work out % of retirement distance used
  -> If >= 80%: send a notification
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

### 7. If yes: Notifications "Send me an email notification"
- Subject: `Time to replace your @{outputs('Shoe_model')}`
- Body: `You have run @{formatNumber(float(outputs('Total_km')),'0.0')} km in your @{outputs('Shoe_model')} (@{formatNumber(float(outputs('Percent_used')),'0')}% of its @{outputs('Retire_km')} km life). Time to order a new pair.`

If no: do nothing.

### 8. Test
1. Save. Flow checker should show no errors.
2. Test > Manually > log a run in the Canvas/model-driven app with **shoe_id 2** -> email arrives.
3. Log a run with **shoe_id 1** -> flow runs, condition = false, no email.
4. Screenshot the run history (one Yes, one No) into `docs/screenshots/`.
5. Delete the two test runs afterwards (or keep them and note it).

## Design notes (talking points)
- **Why Dataverse trigger, not a schedule:** event-driven = alert arrives right after the run that crosses the line.
- **Why FetchXML aggregate:** Dataverse sums server-side; no loop over every run (fewer API calls, faster, fits
  consumption limits).
- **Known limitation:** after 80% every new run in that shoe alerts again. Improvement: add an
  `alert_sent` yes/no column on Shoes and only notify once.
- **Human oversight:** flow notifies; the runner decides. No automatic purchasing.
