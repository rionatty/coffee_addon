COFFEE DEMO - IMPORT FILES
==========================

Before you start
  * Company must be named exactly:  Ideal Commodities (U) Ltd
  * Company abbreviation must be:   ICL
    (the setup wizard suggests "IC(L" - change it to ICL)
  * The company must have NO transactions yet.
  * Enable USD: Currency > USD > tick Enabled > Save.
  * Install the coffee_addon app on the site first: it brings the Goods
    Received Note tab on Purchase Receipt and the Certificate of Analysis
    print format.

STEP 1 - Chart of accounts (Chart of Accounts Importer, not Data Import)
  Search "Chart of Accounts Importer" > choose the company
  > attach 00_chart_of_accounts.xlsx > check the tree it shows > Import.
  This REPLACES the company's chart (and its tax templates): 329 accounts in
  the client's own numbering. Raw material and finished product are apart:
     12010100 Raw Material Stock
        12010101 Robusta FAQ Stock, 12010102 Arabica Parchment Stock
     12010300 Finished Product Stock
        12010310 Robusta Finished Stock > 12010311 Robusta Screen 18 Stock ...
        12010320 Arabica Finished Stock > 12010321 Arabica Screen 18 Stock ...
        12010330 By-products Stock (dust and husks, from both)
  Sales (4101xxxx) and Cost of Sales (5101xxxx) by coffee type and screen.
  What was changed from their file is listed in coa_changes.txt.

STEP 2 - Data Import, in this order, one at a time:
  Data Import > + Add Data Import > Document Type: (below)
  > Import Type: (below) > attach the file > Save > Start Import

   File                                  Document Type                 Import Type
   01_account_update.csv                 Account                       Update Existing Records
   01b_account_insert.csv                Account                       Insert New Records
   02_warehouse_1.csv                    Warehouse                     Insert New Records
   02_warehouse_2.csv                    Warehouse                     Insert New Records
   02_warehouse_3.csv                    Warehouse                     Insert New Records
   03_item_group_0.csv                   Item Group                    Update Existing Records
   03_item_group_1.csv                   Item Group                    Insert New Records
   03_item_group_2.csv                   Item Group                    Insert New Records
   03_item_group_3.csv                   Item Group                    Insert New Records
   04_quality_inspection_parameter.csv   Quality Inspection Parameter  Insert New Records
   05_quality_inspection_template.csv    Quality Inspection Template   Insert New Records
   06_item.csv                           Item                          Insert New Records
   07_price_list.csv                     Price List                    Insert New Records
   08_item_price.csv                     Item Price                    Insert New Records
   09_supplier_group.csv                 Supplier Group                Insert New Records
   10_supplier.csv                       Supplier                      Insert New Records
   11_customer_group.csv                 Customer Group                Insert New Records
   12_customer.csv                       Customer                      Insert New Records
   13_currency_exchange.csv              Currency Exchange             Insert New Records
   14_bom.csv                            BOM                           Insert New Records
                                         (tick "Submit After Import" before Start Import:
                                          only a submitted BOM can be used for production)

  If the preview shows ANY "do not exist" or "missing" message, stop:
    Data Import checks every row before it inserts anything, and a single
    missing value makes it import nothing at all. Each file here only
    refers to records made by the files before it - that is why the stores
    and the item groups come in three files each, one level of the tree at
    a time. So a missing value always means an earlier step is not in:
      a store or group from the same family  -> the file before it (_1, _2);
      a store (... Store - ICL) in 03        -> the 02 files;
      a ledger (NUMBER - Name - ICL)         -> the chart (STEP 1), or the
                                                abbreviation is not ICL.

  Item groups already imported from an earlier version of these files?
    Do not import 03 again. One command puts the tree right - missing groups
    made, misplaced ones moved, every group given its store and ledgers:
      bench --site SITE execute coffee_addon.coffee_addon.demo_setup.item_groups
    (03_item_group_0 makes ERPNext's own "Raw Material" group a parent, so
    the raw coffee groups can sit under it.)

  01 must come right after the chart: it gives the USD export receivable and
  the GBP / USD creditors their account type, which the chart import has to
  leave off (ERPNext would make one of them the company default and refuse
  it).

What it builds
  Stores: Raw Material Stores (Robusta FAQ, Arabica Parchment) and Finished
  Product Stores > Robusta Stores / Arabica Stores (Screen 18, 15, 12,
  Undergrades) and By-products Store. Each store posts to its own ledger.

  Item groups: Raw Material > Raw Robusta, Raw Arabica; Finished Product >
  Robusta Grades > Robusta Grade 18 / 15 / 12 / Undergrades, Arabica Grades
  > ..., By-products. Each line's group carries its store and its three
  ledgers - Stock (the store's own), Revenue and Cost of Sales - so its
  items post there. ERPNext v16 reads Cost of Sales on Delivery Notes and
  Sales Invoices from the group's Default COGS Account; the Default
  Expense Account carries the same ledger for v15. The Default Inventory
  Account is used when item-wise inventory accounts are switched on for
  the company; otherwise the store's ledger, which is the same one.

  01b adds the four ledgers raw coffee needs and the client's chart does
  not have: 41010115 Robusta FAQ Sales, 41010125 Arabica Parchment Sales,
  51010115 Robusta FAQ Cost of Sales, 51010125 Arabica Parchment Cost of
  Sales - for raw coffee sold as it is, without milling.

  Quality control: 14 parameters (moisture, FM, CS, GT, CUT and the screen
  outturns from the GRN; screen retention, defect count, black beans, cup
  quality for export) and 6 templates: Robusta FAQ Intake, Arabica
  Parchment Intake, Screen 18 / 15 / 12 Export, Undergrade Grading. Every
  item is on its template; the export grades need a Quality Inspection
  before delivery. Print that inspection with the "Certificate of
  Analysis" print format. The specifications are demo figures.

  Customers: Export Buyers > 12020101 Export Customers (USD), Export (USD)
  price list, customers billed in USD. Local Buyers > 12020102 Local
  Customers (UGX), Standard Selling, billed in UGX.

  Milling BOMs (14_bom.csv), per 100 kg of raw coffee in:
    Robusta FAQ        -> Screen 15 50.45 kg (the BOM's item), Screen 18 13.2,
                          Screen 12 16.85 (the screens as on the Goods
                          Received Note), BHP 1199 7, Triage 4, Blacks 2,
                          Browns 1.5, Pods 1, Coffee Dust 1.5; 2.5 kg lost.
    Arabica Parchment  -> Screen 15 31 kg, Screen 18 23, Screen 12 14,
                          Triage 5, Blacks 2, Browns 2, Pods 1, Coffee Husks
                          19 (the parchment), Coffee Dust 1; 2 kg lost.
    The other screens are Additional Finished Goods, the undergrades
    Co-Products, dust and husks By-Products. The raw coffee's cost is shared
    by sales value at the demo prices, in whole percentages (Robusta: Screen
    15 56%, 18 16%, 12 18%, BHP 5%, Triage 2%, Blacks/Browns/Pods 1% each);
    by-products carry no cost, so their sale is all margin. A Work Order
    for the main grade consumes the raw coffee in that ratio: 50.45 kg of
    Robusta Screen 15 per 100 kg of FAQ. Yields and shares are demo figures.

  19 items, a demo farmer, prices and a USD rate (demo figures).

All of it in one command instead, if you have the server's shell:
  bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run
