COFFEE DEMO - DATA IMPORT FILES
================================

Import them in this order, one at a time:
  Data Import > + Add Data Import > Document Type: (below) > Import Type: Insert New Records
  > attach the file > Save > Start Import

   File                       Document Type
   01_account.csv             Account
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

Before you start
  * Company must be named exactly:  Ideal Commodities (U) Ltd
  * Company abbreviation must be:   ICL
    If yours is different, find-and-replace " - ICL" with " - <your abbreviation>"
    in files 01, 02 and 03 before importing.
  * Built for ERPNext's Standard chart of accounts (no account numbers).
  * Enable USD: Currency > USD > tick Enabled > Save.

What it builds
  Screen 18, 15 and 12 each get their own active ledgers (Stock, Sales,
  Cost of Sales), their own store, their own item group under Finished
  Goods, and a finished-goods item named for the screen (Robusta Screen 18).
  Undergrades, by-products and raw coffee the same way, plus the GRN 1731
  farmer, an export and a local customer, prices and a USD rate.
  Prices and the USD rate are demo figures.

Same result in one command, if you have the server's shell:
  bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run --kwargs "{'company': 'Ideal Commodities (U) Ltd'}"
