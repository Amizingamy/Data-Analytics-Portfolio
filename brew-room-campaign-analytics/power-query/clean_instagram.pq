// Power Query (M): clean the Instagram export  ->  clean_instagram
// Edit FolderPath to the folder that holds your CSV files (keep the final backslash).
let
    FolderPath = "C:\Users\YOURNAME\Documents\Brew Room\",

    // Columns = 7 matters: the first two junk lines only have one field
    Raw = Csv.Document(File.Contents(FolderPath & "instagram_export.csv"),
            [Delimiter = ",", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Skipped = Table.Skip(Raw, 2),                       // two junk lines above the header
    Promoted = Table.PromoteHeaders(Skipped, [PromoteAllScalars = true]),
    Renamed = Table.RenameColumns(Promoted,
        List.Zip({Table.ColumnNames(Promoted),
                  {"date", "post_theme", "reach", "likes", "saves", "comments", "story_replies"}})),
    Trimmed = Table.TransformColumns(Renamed,
        List.Transform(Table.ColumnNames(Renamed), each {_, each Text.Trim(_), type text})),

    NoTotal = Table.SelectRows(Trimmed, each Text.Upper([date]) <> "TOTAL"),

    Dates = Table.TransformColumns(NoTotal, {{"date", each
        if Text.Contains(_, "/")
        then Date.ToText(Date.FromText(_, [Format = "dd/MM/yyyy", Culture = "en-GB"]), "yyyy-MM-dd")
        else _, type text}}),

    WithKey = Table.AddColumn(Dates, "theme_key", each Text.Upper([post_theme]), type text),
    LookupRaw = Csv.Document(File.Contents(FolderPath & "post_theme_lookup.csv"),
            [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Lookup = Table.RenameColumns(Table.PromoteHeaders(LookupRaw, [PromoteAllScalars = true]),
                                 {{"post_theme", "clean_theme"}}),
    Joined = Table.NestedJoin(WithKey, {"theme_key"}, Lookup, {"raw_key"}, "lk", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Joined, "lk", {"clean_theme"}),
    Themed = Table.RemoveColumns(
                Table.RenameColumns(Table.RemoveColumns(Expanded, {"post_theme"}), {{"clean_theme", "post_theme"}}),
                {"theme_key"}),

    Numbers = Table.TransformColumns(Themed,
        List.Transform({"reach", "likes", "saves", "comments", "story_replies"},
                       each {_, each Number.FromText(_), Int64.Type})),

    Final = Table.Sort(
        Table.SelectColumns(Numbers, {"date", "post_theme", "reach", "likes", "saves", "comments", "story_replies"}),
        {{"date", Order.Ascending}})
in
    Final
