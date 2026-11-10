// Power Query (M) for the Marathon Tracker model.
// In Power BI Desktop: Home > Transform data > New Source > Blank Query > Advanced Editor,
// paste ONE query at a time, and rename the query to the name in the header comment.
// Site URL: https://pulpente.sharepoint.com

// ============================================================ Runs
let
    Source   = SharePoint.Tables("https://pulpente.sharepoint.com", [ApiVersion = 15]),
    Items    = Source{[Title = "Runs"]}[Items],
    // SharePoint exposes CSV-imported columns as field_1, field_2, ... in CSV order.
    Renamed  = Table.RenameColumns(Items,
                 {{"Title","run_id"},{"field_1","run_date"},{"field_2","run_type"},{"field_3","distance_km"},
                  {"field_4","duration_min"},{"field_5","avg_pace"},{"field_6","avg_hr"},{"field_7","max_hr"},
                  {"field_8","elevation_m"},{"field_9","shoe_id"},{"field_10","weather"},{"field_11","temp_c"},
                  {"field_12","rpe"}}, MissingField.Ignore),
    Selected = Table.SelectColumns(Renamed,
                 {"run_id","run_date","run_type","distance_km","duration_min","avg_pace","avg_hr",
                  "max_hr","elevation_m","shoe_id","weather","temp_c","rpe"}, MissingField.UseNull),
    // SharePoint shows midnight-UTC dates shifted back by a day (e.g. 1/5/2026 4:00 PM).
    // Adding 12 hours then taking the date gives the intended day whatever the offset.
    DateFix  = Table.AddColumn(Selected, "run_day", each Date.From(DateTime.From([run_date]) + #duration(0,12,0,0)), type date),
    PaceSec  = Table.AddColumn(DateFix, "pace_sec", each
                 let p = Text.Split(Text.From([avg_pace]), ":")
                 in if List.Count(p) = 2 then Number.FromText(p{0}) * 60 + Number.FromText(p{1}) else null, type number),
    Typed    = Table.TransformColumnTypes(PaceSec,
                 {{"run_id", Int64.Type}, {"distance_km", type number}, {"duration_min", type number},
                  {"avg_hr", Int64.Type}, {"max_hr", Int64.Type}, {"elevation_m", Int64.Type},
                  {"shoe_id", Int64.Type}, {"temp_c", Int64.Type}, {"rpe", Int64.Type}}),
    Result   = Table.RemoveColumns(Typed, {"run_date"})
in
    Result

// ============================================================ Races
let
    Source   = SharePoint.Tables("https://pulpente.sharepoint.com", [ApiVersion = 15]),
    Items    = Source{[Title = "Races"]}[Items],
    Renamed  = Table.RenameColumns(Items,
                 {{"Title","race_id"},{"field_1","race_name"},{"field_2","race_date"},{"field_3","distance_km"},
                  {"field_4","goal_time_sec"},{"field_5","finish_time_sec"},{"field_6","overall_position"},
                  {"field_7","location"},{"field_8","split_5k"},{"field_9","split_10k"},{"field_10","split_15k"},
                  {"field_11","split_20k"},{"field_12","split_25k"},{"field_13","split_30k"},
                  {"field_14","split_35k"},{"field_15","split_40k"}}, MissingField.Ignore),
    Selected = Table.SelectColumns(Renamed,
                 {"race_id","race_name","race_date","distance_km","goal_time_sec","finish_time_sec",
                  "overall_position","location","split_5k","split_10k","split_15k","split_20k",
                  "split_25k","split_30k","split_35k","split_40k"}, MissingField.UseNull),
    DateFix  = Table.AddColumn(Selected, "race_day", each Date.From(DateTime.From([race_date]) + #duration(0,12,0,0)), type date),
    // Empty split cells were imported as 0; turn them back into blanks.
    NoZeros  = Table.ReplaceValue(DateFix, 0, null, Replacer.ReplaceValue,
                 {"split_5k","split_10k","split_15k","split_20k","split_25k","split_30k","split_35k","split_40k"}),
    Dropped  = Table.RemoveColumns(NoZeros, {"race_date"}),
    Result   = Table.TransformColumnTypes(Dropped,
                 {{"race_id", Int64.Type}, {"distance_km", type number}, {"goal_time_sec", Int64.Type},
                  {"finish_time_sec", Int64.Type}, {"overall_position", Int64.Type},
                  {"split_5k", Int64.Type}, {"split_10k", Int64.Type}, {"split_15k", Int64.Type},
                  {"split_20k", Int64.Type}, {"split_25k", Int64.Type}, {"split_30k", Int64.Type},
                  {"split_35k", Int64.Type}, {"split_40k", Int64.Type}})
in
    Result

// ============================================================ Shoes
let
    Source   = SharePoint.Tables("https://pulpente.sharepoint.com", [ApiVersion = 15]),
    Items    = Source{[Title = "Shoes"]}[Items],
    Renamed  = Table.RenameColumns(Items,
                 {{"Title","shoe_id"},{"field_1","model"},{"field_2","purchase_date"},{"field_3","retire_km"}},
                 MissingField.Ignore),
    Selected = Table.SelectColumns(Renamed, {"shoe_id","model","purchase_date","retire_km"}, MissingField.UseNull),
    Typed    = Table.TransformColumnTypes(Selected, {{"shoe_id", Int64.Type}, {"retire_km", Int64.Type}}),
    DateFix  = Table.AddColumn(Typed, "purchase_day", each Date.From(DateTime.From([purchase_date]) + #duration(0,12,0,0)), type date),
    Result   = Table.RemoveColumns(DateFix, {"purchase_date"})
in
    Result

// ============================================================ RaceSplits
// Long format for the pacing chart. Create AFTER Races, referencing it.
let
    Source    = Races,
    Cols      = {"race_id","race_name","race_day"},
    Unpivoted = Table.UnpivotOtherColumns(
                  Table.SelectColumns(Source, Cols & {"split_5k","split_10k","split_15k","split_20k","split_25k","split_30k","split_35k","split_40k"}),
                  Cols, "split", "split_sec"),
    Clean     = Table.SelectRows(Unpivoted, each [split_sec] <> null),
    Km        = Table.AddColumn(Clean, "km_mark", each Number.FromText(Text.BetweenDelimiters([split], "_", "k")), Int64.Type),
    Result    = Table.TransformColumnTypes(Km, {{"race_id", Int64.Type}, {"split_sec", Int64.Type}})
in
    Result

// ============================================================ Recovery  (no SharePoint list yet: load the CSV)
// Change the path if you moved the repo.
let
    Source  = Csv.Document(File.Contents("C:\Users\Mo_z_\Desktop\Projects_2026\quizGame\marathon-tracker\data\generated\fact_recovery.csv"),
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers,
                {{"date", type date}, {"weight_kg", type number}, {"resting_hr", Int64.Type},
                 {"sleep_hours", type number}, {"hrv_ms", Int64.Type}, {"soreness", Int64.Type}}, "en-US")
in
    Typed
