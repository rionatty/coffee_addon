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
   02_warehouse.csv                      Warehouse                     Insert New Records
   03_item_group.csv                     Item Group                    Insert New Records
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
  > ..., By-products. Each line's group carries its store and its Sales and
  Cost of Sales ledgers, so its items post there.

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

  19 items, the GRN 1731 farmer, prices and a USD rate (demo figures).

All of it in one command instead, if you have the server's shell:
  bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run
