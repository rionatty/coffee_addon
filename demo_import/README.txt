COFFEE DEMO - IMPORT FILES
==========================

Before you start
  * Company must be named exactly:  Ideal Commodities (U) Ltd
  * Company abbreviation must be:   ICL
    (the setup wizard suggests "IC(L" - change it to ICL)
  * Do this on a company with NO transactions yet.
  * Enable USD: Currency > USD > tick Enabled > Save.

STEP 1 - Chart of accounts (Chart of Accounts Importer, not Data Import)
  Search "Chart of Accounts Importer" > choose the company
  > attach 00_chart_of_accounts.xlsx > check the tree it shows > Import.
  This REPLACES the company's chart (and its tax templates) with this one:
  309 accounts, the client's own numbering, with Screen 18 / 15 / 12 as
  their own Stock, Sales and Cost of Sales ledgers. What was changed from
  their file is listed in coa_changes.txt.

STEP 2 - Masters (Data Import), in this order, one at a time:
  Data Import > + Add Data Import > Document Type: (below)
  > Import Type: Insert New Records > attach the file > Save > Start Import

   File                       Document Type
   02_warehouse.csv           Warehouse
   03_item_group.csv          Item Group
   04_item.csv                Item
   05_price_list.csv          Price List
   06_item_price.csv          Item Price
   07_supplier_group.csv      Supplier Group
   08_supplier.csv            Supplier
   09_customer_group.csv      Customer Group
   10_customer.csv            Customer
   11_currency_exchange.csv   Currency Exchange

  (There is no 01: the ledgers come from the chart in step 1.)

What it builds
  Each screen has its own store, posting to its own Stock ledger
  (e.g. Screen 18 Store -> 12010102 - Screen 18 Stock), its own item group
  under Finished Goods defaulting 41010101 Screen 18 Sales and
  51010101 Screen 18 Cost of Sales, and a finished-goods item named for
  the screen (Robusta Screen 18). Undergrades, by-products and raw coffee
  the same way, plus the GRN 1731 farmer, an export and a local customer,
  prices and a USD rate. Prices and the USD rate are demo figures.

Same masters in one command, if you have the server's shell (run it after step 1):
  bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run --kwargs "{'company': 'Ideal Commodities (U) Ltd'}"
