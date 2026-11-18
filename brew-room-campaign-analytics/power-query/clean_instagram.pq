// Power Query (M): clean the Instagram export  ->  clean_instagram
// Edit FolderPath to the folder that holds your CSV files (keep the final backslash).
let
    FolderPath = "C:\Users\YOURNAME\Documents\Brew Room\",

    FixDate = (t as text) as text =>
        if Text.Contains(t, "/")
        then Date.ToText(Date.FromText(t, [Format = "dd/MM/yyyy", Culture = "en-GB"]), "yyyy-MM-dd")
        else t,

    // Columns = 7 matters: the first two junk lines only have one field
    Raw = Csv.Document(File.Contents(FolderPath & "instagram_export.csv"), [Delimiter = ",", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Skipped = Table.Skip(Raw, 2),
    Promoted = Table.PromoteHeaders(Skipped, [PromoteAllScalars = true]),
    NewNames = {"date", "post_theme", "reach", "likes", "saves", "comments", "story_replies"},
    Renamed = Table.RenameColumns(Promoted, List.Zip({Table.ColumnNames(Promoted), NewNames})),
    Trimmed = Table.TransformColumns(Renamed, List.Transform(NewNames, each {_, Text.Trim, type text})),

    NoTotal = Table.SelectRows(Trimmed, each Text.Upper([date]) <> "TOTAL"),
    Dates = Table.TransformColumns(NoTotal, {{"date", FixDate, type text}}),

    WithKey = Table.AddColumn(Dates, "theme_key", each Text.Upper([post_theme]), type text),
    LookupRaw = Csv.Document(File.Contents(FolderPath & "post_theme_lookup.csv"), [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    LookupHeaders = Table.PromoteHeaders(LookupRaw, [PromoteAllScalars = true]),
    Lookup = Table.RenameColumns(LookupHeaders, {{"post_theme", "clean_theme"}}),
    Joined = Table.NestedJoin(WithKey, {"theme_key"}, Lookup, {"raw_key"}, "lk", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Joined, "lk", {"clean_theme"}),
    Dropped = Table.RemoveColumns(Expanded, {"post_theme", "theme_key"}),
    Themed = Table.RenameColumns(Dropped, {{"clean_theme", "post_theme"}}),

    Numbers = Table.TransformColumns(Themed, {
        {"reach", Number.FromText, Int64.Type},
        {"likes", Number.FromText, Int64.Type},
        {"saves", Number.FromText, Int64.Type},
        {"comments", Number.FromText, Int64.Type},
        {"story_replies", Number.FromText, Int64.Type}}),

    Picked = Table.SelectColumns(Numbers, NewNames),
    Final = Table.Sort(Picked, {{"date", Order.Ascending}})
in
    Final
