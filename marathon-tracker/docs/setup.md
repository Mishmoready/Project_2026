# Environment setup

## Installed locally
- Python 3.12 (data generator)
- Power BI Desktop
- .NET 8 SDK
- Power Platform CLI (`pac`), via the VS Code "Power Platform Tools" extension

## Tenant
- Microsoft 365 E3 trial, tenant `pulpente.onmicrosoft.com`
- MFA registered (security defaults on). Note: security defaults block device-code sign-in,
  so `pac auth create` must be run WITHOUT `--deviceCode` (interactive browser dialog).

## Decision log
- 2026-11-09: Dataverse could not be provisioned. Tenant has no Power Apps plan
  ("A self-service signup plan is required"; `pac admin create` says "no CRM license"),
  and the Developer Plan sign-up did not create an environment.
- Pivot: use **SharePoint lists** (included in E3) as the data store for the Canvas App,
  Power Automate flows and Power BI. The Dataverse design stays documented in
  [data-model.md](data-model.md) so it can be added later if licensing is fixed.

## SharePoint lists (create from the CSVs in data/generated)
| List | Source CSV |
|---|---|
| Runs | fact_runs.csv |
| Races | fact_races.csv |
| Shoes | dim_shoes.csv |
| Recovery (optional) | fact_recovery.csv |

In SharePoint: New > List > From CSV, upload the file, check the column types, and Create.

## Version control
All files are in this repo. Canvas App and flow exports go in `powerplatform/`.
