## Coffee Addon

Coffee processing for ERPNext, built for a buyer who takes coffee from
farmers and agents, grades it and exports it.

### Goods Received Note

The paper note that is written when a truck delivers is kept on ERPNext's
own **Purchase Receipt**, on a Goods Received Note tab: the note and truck
details, the quality block (moisture, defects, yields), the bag-by-bag
weight note, and the weight ladder that ends in what is owed:

```
Total kgs  −  less bags  =  sub gross  −  reductions  =  net weight  ×  price = amount
```

The weight note rows add up to the total, the ladder works itself out as
the weights are typed, and the amount is written out in words the way the
book does it. Reductions are entered in kilos by the quality controller.

When the note is filled in and the receipt has a single item row, that row
takes the net weight as its quantity and the price paid as its rate, so
the coffee reaches the store and the supplier is owed the same figures the
note shows.

### Demo books

`demo_import/` holds the client's chart of accounts (for the Chart of
Accounts Importer) and the master data as Data Import files, with a
README giving the order. Raw material and finished product are apart in
the chart, the stores and the item groups; finished product is split by
coffee type (Robusta, Arabica) and then by screen, each screen with its own
Stock, Sales and Cost of Sales ledgers. Quality inspection parameters and
templates map every item, and export grades need an inspection before
delivery. Export customers are billed in USD to a USD receivable.

The same files, through ERPNext's own importers, in one command:

```bash
bench --site your-site execute coffee_addon.coffee_addon.demo_setup.run
```

### Certificate of Analysis

A print format for Quality Inspection: the specification of each parameter,
the result (the mean of the readings), whether it passed, and the
inspection's conclusion, for the buyer of each lot.

### Install

```bash
bench get-app --branch main https://github.com/rionatty/coffee_addon.git
bench --site your-site install-app coffee_addon
bench --site your-site migrate
```

#### License

MIT
