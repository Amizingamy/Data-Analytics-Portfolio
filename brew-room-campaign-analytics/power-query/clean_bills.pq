// Power Query (M): clean the till export  ->  clean_transactions
// Edit FolderPath to the folder that holds your five CSV files (keep the final backslash).
let
    FolderPath = "C:\Users\YOURNAME\Documents\Brew Room\",

    Raw = Csv.Document(File.Contents(FolderPath & "pos_bills.csv"),
            [Delimiter = ",", Columns = 6, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Raw, [PromoteAllScalars = true]),
    Renamed = Table.RenameColumns(Promoted,
        {{"Bill No", "order_id"}, {"Bill Date", "date"}, {"Customer", "customer_id"},
         {"Item", "item"}, {"Qty", "quantity"}, {"Amount", "amount"}}),

    // 1. trim spaces in every column
    Trimmed = Table.TransformColumns(Renamed,
        List.Transform(Table.ColumnNames(Renamed), each {_, each Text.Trim(_), type text})),

    // 2. drop blank lines and staff test bills
    NoBlank = Table.SelectRows(Trimmed, each [order_id] <> null and [order_id] <> ""),
    NoTest = Table.SelectRows(NoBlank, each Text.Upper([item]) <> "TEST ORDER"),

    // 3. drop duplicate bills
    Dedup = Table.Distinct(NoTest, {"order_id"}),

    // 4. standardise product names using the lookup table
    WithKey = Table.AddColumn(Dedup, "item_key", each Text.Upper([item]), type text),
    LookupRaw = Csv.Document(File.Contents(FolderPath & "product_lookup.csv"),
            [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Lookup = Table.PromoteHeaders(LookupRaw, [PromoteAllScalars = true]),
    Joined = Table.NestedJoin(WithKey, {"item_key"}, Lookup, {"raw_key"}, "lk", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Joined, "lk", {"product"}),

    // 5. one date format (yyyy-mm-dd), numbers without "Rs"/"INR", whole-number quantity
    Dates = Table.TransformColumns(Expanded, {{"date", each
        if Text.Contains(_, "/")
        then Date.ToText(Date.FromText(_, [Format = "dd/MM/yyyy", Culture = "en-GB"]), "yyyy-MM-dd")
        else _, type text}}),
    Customer = Table.TransformColumns(Dates, {{"customer_id", Text.Upper, type text}}),
    Numbers = Table.TransformColumns(Customer, {
        {"amount", each Number.Round(Number.FromText(Text.Select(_, {"0".."9", "."})), 0), Int64.Type},
        {"quantity", each Number.Round(Number.FromText(_), 0), Int64.Type}}),

    Final = Table.Sort(
        Table.SelectColumns(Numbers, {"order_id", "date", "customer_id", "product", "quantity", "amount"}),
        {{"date", Order.Ascending}, {"customer_id", Order.Ascending}, {"product", Order.Ascending}})
in
    Final
