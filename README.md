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

### Install

```bash
bench get-app --branch main https://github.com/rionatty/coffee_addon.git
bench --site your-site install-app coffee_addon
bench --site your-site migrate
```

#### License

MIT
