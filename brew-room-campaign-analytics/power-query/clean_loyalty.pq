// Power Query (M): clean the loyalty sign-ups  ->  clean_loyalty
// Edit FolderPath to the folder that holds your CSV files (keep the final backslash).
let
    FolderPath = "C:\Users\YOURNAME\Documents\Brew Room\",

    Raw = Csv.Document(File.Contents(FolderPath & "loyalty_signups.csv"),
            [Delimiter = ",", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Raw, [PromoteAllScalars = true]),
    Renamed = Table.RenameColumns(Promoted,
        List.Zip({Table.ColumnNames(Promoted),
                  {"member_id", "signup_date", "tier", "visits_post_signup",
                   "total_spend_post_signup", "redeemed_reward", "referred_a_friend"}})),
    Trimmed = Table.TransformColumns(Renamed,
        List.Transform(Table.ColumnNames(Renamed), each {_, each Text.Trim(_), type text})),

    Dedup = Table.Distinct(Trimmed, {"member_id"}),

    ToFlag = (t as nullable text) as logical => List.Contains({"Y", "YES", "TRUE"}, Text.Upper(Text.Trim(t))),

    Cleaned = Table.TransformColumns(Dedup, {
        {"signup_date", each
            if Text.Contains(_, "/")
            then Date.ToText(Date.FromText(_, [Format = "dd/MM/yyyy", Culture = "en-GB"]), "yyyy-MM-dd")
            else _, type text},
        {"tier", Text.Proper, type text},
        {"visits_post_signup", each Number.FromText(_), Int64.Type},
        {"total_spend_post_signup", each Number.Round(Number.FromText(Text.Select(_, {"0".."9", "."})), 0), Int64.Type},
        {"redeemed_reward", ToFlag, type logical},
        {"referred_a_friend", ToFlag, type logical}}),

    Final = Table.Sort(Cleaned, {{"member_id", Order.Ascending}})
in
    Final
