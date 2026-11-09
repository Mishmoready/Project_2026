# Marathon Tracker

A portfolio project that uses marathon training to show end-to-end Microsoft Power Platform skills:
apps, automation, data modelling, Power BI, AI agents, integration and governance.

> Status: scaffolded. Data is synthetic (seeded) until real Strava/Garmin data is connected.

## Roadmap

| # | Stage | Folder | Status |
|---|-------|--------|--------|
| 1 | Synthetic data + Power BI semantic model and report | `scripts/`, `powerbi/` | In progress |
| 2 | Dataverse tables + Canvas App to log runs | `powerplatform/solution/` | Todo |
| 3 | Power Automate flows (weekly summary, shoe-wear alert) | `powerplatform/flows/` | Todo |
| 4 | Copilot Studio agent ("how is my training load?") | `powerplatform/copilot/` | Todo |
| 5 | Integration: Strava API, SharePoint plan docs | `docs/` | Todo |
| 6 | Governance: environments, ALM, handover docs | `docs/` | Todo |

## Quick start

```powershell
cd marathon-tracker
python scripts/generate_data.py            # writes CSVs to data/generated
```

Then open Power BI Desktop, Get Data > Text/CSV, and load the files in `data/generated`.
See [docs/data-model.md](docs/data-model.md) for the relationships and [docs/setup.md](docs/setup.md) for environment setup.

## Layout

```
data/generated/    synthetic CSVs (git-tracked, reproducible via seed)
data/raw/          real exports (git-ignored)
scripts/           data generator
powerbi/           .pbix / PBIP project, DAX measures
powerplatform/     solution, flows, Copilot Studio exports
sql/               warehouse/lakehouse DDL
docs/              specs, data model, setup, handover
```
