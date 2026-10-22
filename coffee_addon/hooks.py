app_name = "coffee_addon"
app_title = "Coffee Addon"
app_publisher = "CyveTech"
app_description = "Coffee processing for ERPNext: the Goods Received Note, grades and yields"
app_email = "42210367+rionatty@users.noreply.github.com"
app_license = "mit"

# Everything here builds on ERPNext's buying and stock.
required_apps = ["erpnext"]

# The Goods Received Note adds itself up on the form as it is typed.
doctype_js = {
	"Purchase Receipt": "public/js/purchase_receipt.js",
}

doc_events = {
	"Purchase Receipt": {
		# Before ERPNext totals the receipt, so the item line carries the
		# note's net weight and price when ERPNext works out the amounts.
		"before_validate": "coffee_addon.coffee_addon.goods_received_note.before_validate",
	},
}

# The Goods Received Note tab on Purchase Receipt: fixtures/custom_field.json,
# installed and updated on every migrate.
fixtures = [
	{"dt": "Custom Field", "filters": [["module", "=", "Coffee Addon"]]},
]
