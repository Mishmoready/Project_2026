# Environment setup

## Installed locally
- Python 3.12 (data generator)
- Power BI Desktop

## Needs a sign-up (cloud, cannot be installed)
1. **Microsoft 365 Developer Program** (developer.microsoft.com/microsoft-365/dev-program): free sandbox tenant, if eligible.
   Fallback: **Power Apps Developer Plan** (free, personal Dataverse environment, requires a work/school account)
   or a 30-day Power Apps / Fabric trial.
2. In the tenant, open make.powerapps.com and create two environments: `Dev` and `Test` (for ALM practice).
3. **Power Platform CLI (`pac`)**: not on winget. Easiest route is the "Power Platform Tools" VS Code extension,
   or install the .NET SDK and run `dotnet tool install --global Microsoft.PowerApps.CLI.Tool`.
4. Publish the Power BI report to the Power BI Service using the same account.

## Version control
Export the Dataverse solution unmanaged and unpack it into `powerplatform/solution/` using `pac solution unpack`.
