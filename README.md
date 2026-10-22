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

### Demo masters

One command builds the books for a coffee demo, and is safe to run again:

```bash
bench --site your-site execute coffee_addon.coffee_addon.demo_setup.run --kwargs "{'company': 'Your Company'}"
```

Screen 18, 15 and 12 each get their own active Stock, Sales and Cost of
Sales ledgers, their own store and item group, and a finished-goods item
named for the screen (Robusta Screen 18). Undergrades, by-products and the
raw coffee get the same treatment, plus a farmer, two customers, prices and
a USD rate. See `coffee_addon/coffee_addon/demo_setup.py`.

### Install

```bash
bench get-app --branch main https://github.com/rionatty/coffee_addon.git
bench --site your-site install-app coffee_addon
bench --site your-site migrate
```

#### License

MIT
