# Copyright (c) 2026, CyveTech and contributors
# For license information, please see license.txt

"""The coffee demo's masters, built in one command:

	bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run
	bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run --kwargs "{'company': 'Your Company'}"

Each screen is its own line through the books. Screen 18, 15 and 12 each get
	* their own active ledgers: Screen 18 Stock, Screen 18 Sales and
	  Screen 18 Cost of Sales;
	* their own store, whose stock posts to that Stock ledger;
	* their own item group under Finished Goods, which defaults the store and
	  the Sales and Cost of Sales ledgers onto every document;
	* a finished-goods item carrying the screen in its name: Robusta Screen 18.
So the balance sheet shows the coffee held per screen and the profit and
loss the margin per screen, with nothing to pick on each document.

The undergrades and the by-products are one line each in the same way, and
the raw coffee bought at the weighbridge has its own store and ledger. Also
made: the farmer on GRN 1731 as a supplier, an export and a local customer,
buying and selling prices, and a USD rate. The prices and the rate are demo
figures — change them in the desk as you like.

Safe to run again: anything that already exists is left exactly as it is.
"""

from collections import namedtuple

import frappe
from frappe import _
from frappe.utils import nowdate

Line = namedtuple("Line", "group parent store stock sales cost items")

FINISHED_GOODS = "Finished Goods"
ROOT_GROUP = "All Item Groups"
RAW_COFFEE_GROUP = "Raw Coffee"

LINES = (
	Line(RAW_COFFEE_GROUP, ROOT_GROUP, "Raw Coffee Store", "Raw Coffee Stock", None, None, ("Robusta FAQ",)),
	Line("Screen 18", FINISHED_GOODS, "Screen 18 Store", "Screen 18 Stock", "Screen 18 Sales",
		"Screen 18 Cost of Sales", ("Robusta Screen 18",)),
	Line("Screen 15", FINISHED_GOODS, "Screen 15 Store", "Screen 15 Stock", "Screen 15 Sales",
		"Screen 15 Cost of Sales", ("Robusta Screen 15",)),
	Line("Screen 12", FINISHED_GOODS, "Screen 12 Store", "Screen 12 Stock", "Screen 12 Sales",
		"Screen 12 Cost of Sales", ("Robusta Screen 12",)),
	# The five undergrades. 1199 is on the GRN's yields; rename the others to
	# the client's own names once they are confirmed.
	Line("Undergrades", FINISHED_GOODS, "Undergrades Store", "Undergrades Stock", "Undergrade Sales",
		"Undergrade Cost of Sales",
		("Robusta BHP 1199", "Robusta Triage", "Robusta Blacks", "Robusta Browns", "Robusta Pods")),
	Line("By-products", ROOT_GROUP, "By-products Store", "By-products Stock", "By-product Sales",
		"By-product Cost of Sales", ("Coffee Dust", "Coffee Husks")),
)

UOM = "Kg"

BUYING_PRICE_LIST = "Standard Buying"
SELLING_PRICE_LIST = "Standard Selling"
EXPORT_PRICE_LIST = "Export (USD)"

# Demo figures. The buying price is the one paid on GRN 1731.
BUYING_PRICES = {"Robusta FAQ": 11800}
EXPORT_PRICES = {
	"Robusta Screen 18": 5.20,
	"Robusta Screen 15": 4.95,
	"Robusta Screen 12": 4.60,
	"Robusta BHP 1199": 3.10,
	"Robusta Triage": 2.60,
	"Robusta Blacks": 2.20,
	"Robusta Browns": 2.40,
	"Robusta Pods": 1.80,
}
LOCAL_PRICES = {"Coffee Dust": 1500, "Coffee Husks": 100}
USD_RATE = 3650

SUPPLIER_GROUP = "Farmers"
SUPPLIER = "Ssekuna George"
CUSTOMERS = (
	("Export Buyer (Demo)", "Export Buyers", EXPORT_PRICE_LIST),
	("Local Buyer (Demo)", "Local Buyers", SELLING_PRICE_LIST),
)


class Log:
	def __init__(self):
		self.made = []
		self.kept = []

	def note(self, created, doctype, name):
		(self.made if created else self.kept).append(f"{doctype}: {name}")
		return name


def run(company=None):
	import erpnext

	company = company or erpnext.get_default_company()
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(
			_("Name the company to set up: --kwargs \"{'company': 'Your Company'}\"."),
			title=_("Coffee demo"),
		)

	log = Log()
	currency = frappe.get_cached_value("Company", company, "default_currency")
	parents = ledger_parents(company)

	ensure_uom(log)
	ensure_item_group(log, FINISHED_GOODS, ROOT_GROUP, is_group=1)

	for line in LINES:
		stock = ensure_account(log, company, line.stock, parents["stock"], "Stock")
		sales = line.sales and ensure_account(log, company, line.sales, parents["income"], "Income Account")
		cost = line.cost and ensure_account(log, company, line.cost, parents["cost"], "Cost of Goods Sold")
		store = ensure_warehouse(log, company, line.store, stock)
		ensure_item_group(
			log,
			line.group,
			line.parent,
			defaults={"company": company, "default_warehouse": store, "income_account": sales, "expense_account": cost},
		)
		for item_code in line.items:
			ensure_item(log, item_code, line.group, sells=bool(line.sales), buys=line.group == RAW_COFFEE_GROUP)

	ensure_price_list(log, BUYING_PRICE_LIST, currency, buying=1)
	ensure_price_list(log, SELLING_PRICE_LIST, currency, selling=1)
	ensure_price_list(log, EXPORT_PRICE_LIST, "USD", selling=1)
	for prices, price_list in (
		(BUYING_PRICES, BUYING_PRICE_LIST),
		(EXPORT_PRICES, EXPORT_PRICE_LIST),
		(LOCAL_PRICES, SELLING_PRICE_LIST),
	):
		for item_code, rate in prices.items():
			ensure_item_price(log, item_code, price_list, rate)

	ensure_usd_rate(log, currency)
	ensure_parties(log)

	frappe.db.commit()
	print(f"Coffee demo for {company}: {len(log.made)} made, {len(log.kept)} already there.")
	for entry in log.made:
		print("  made  ", entry)
	return {"made": log.made, "kept": log.kept}


def ledger_parents(company):
	"""The group accounts the new ledgers go under: beside the company's own
	stock, sales and cost of goods sold ledgers."""
	defaults = frappe.get_cached_value(
		"Company",
		company,
		["default_inventory_account", "default_income_account", "default_expense_account"],
		as_dict=True,
	)

	def parent_of(account, *group_names):
		parent = account and frappe.db.get_value("Account", account, "parent_account")
		if parent:
			return parent
		for account_name in group_names:
			found = frappe.db.get_value("Account", {"company": company, "is_group": 1, "account_name": account_name})
			if found:
				return found
		frappe.throw(
			_("{0} has no {1} account to put the coffee ledgers beside. Set it on the Company first.").format(
				company, group_names[0]
			),
			title=_("Coffee demo"),
		)

	return {
		"stock": parent_of(defaults.default_inventory_account, "Stock Assets"),
		"income": parent_of(defaults.default_income_account, "Direct Income", "Income"),
		"cost": parent_of(defaults.default_expense_account, "Stock Expenses", "Direct Expenses"),
	}


def ensure_uom(log):
	if frappe.db.exists("UOM", UOM):
		return log.note(False, "UOM", UOM)
	frappe.get_doc({"doctype": "UOM", "uom_name": UOM}).insert(ignore_permissions=True)
	return log.note(True, "UOM", UOM)


def ensure_account(log, company, account_name, parent, account_type):
	existing = frappe.db.get_value("Account", {"company": company, "account_name": account_name})
	if existing:
		return log.note(False, "Account", existing)
	doc = frappe.get_doc({
		"doctype": "Account",
		"company": company,
		"account_name": account_name,
		"parent_account": parent,
		"is_group": 0,
		"account_type": account_type,
	}).insert(ignore_permissions=True)
	return log.note(True, "Account", doc.name)


def ensure_warehouse(log, company, warehouse_name, account):
	existing = frappe.db.get_value("Warehouse", {"company": company, "warehouse_name": warehouse_name})
	if existing:
		return log.note(False, "Warehouse", existing)
	root = frappe.get_all(
		"Warehouse", filters={"company": company, "is_group": 1}, pluck="name", order_by="lft asc", limit=1
	)
	doc = frappe.get_doc({
		"doctype": "Warehouse",
		"warehouse_name": warehouse_name,
		"company": company,
		"parent_warehouse": root[0] if root else None,
		"is_group": 0,
		"account": account,
	}).insert(ignore_permissions=True)
	return log.note(True, "Warehouse", doc.name)


def ensure_item_group(log, name, parent, is_group=0, defaults=None):
	created = not frappe.db.exists("Item Group", name)
	if created:
		doc = frappe.get_doc({
			"doctype": "Item Group",
			"item_group_name": name,
			"parent_item_group": parent,
			"is_group": is_group,
		})
	else:
		doc = frappe.get_doc("Item Group", name)

	# Only add this company's defaults when the group has none for it, so
	# defaults someone has set in the desk are never overwritten.
	changed = False
	if defaults and not any(row.company == defaults["company"] for row in doc.get("item_group_defaults") or []):
		doc.append("item_group_defaults", {key: value for key, value in defaults.items() if value})
		changed = True

	if created:
		doc.insert(ignore_permissions=True)
	elif changed:
		doc.save(ignore_permissions=True)
	return log.note(created or changed, "Item Group", name)


def ensure_item(log, item_code, item_group, sells, buys):
	if frappe.db.exists("Item", item_code):
		return log.note(False, "Item", item_code)
	frappe.get_doc({
		"doctype": "Item",
		"item_code": item_code,
		"item_name": item_code,
		"description": item_code,
		"item_group": item_group,
		"stock_uom": UOM,
		"is_stock_item": 1,
		"include_item_in_manufacturing": 1,
		"is_sales_item": int(sells),
		"is_purchase_item": int(buys),
	}).insert(ignore_permissions=True)
	return log.note(True, "Item", item_code)


def ensure_price_list(log, name, currency, buying=0, selling=0):
	if frappe.db.exists("Price List", name):
		return log.note(False, "Price List", name)
	frappe.get_doc({
		"doctype": "Price List",
		"price_list_name": name,
		"currency": currency,
		"buying": buying,
		"selling": selling,
		"enabled": 1,
	}).insert(ignore_permissions=True)
	return log.note(True, "Price List", name)


def ensure_item_price(log, item_code, price_list, rate):
	label = f"{item_code} @ {price_list}"
	if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list}):
		return log.note(False, "Item Price", label)
	frappe.get_doc({
		"doctype": "Item Price",
		"item_code": item_code,
		"price_list": price_list,
		"price_list_rate": rate,
	}).insert(ignore_permissions=True)
	return log.note(True, "Item Price", label)


def ensure_usd_rate(log, currency):
	if currency == "USD":
		return
	if frappe.db.exists("Currency", "USD") and not frappe.db.get_value("Currency", "USD", "enabled"):
		frappe.db.set_value("Currency", "USD", "enabled", 1)

	label = f"USD -> {currency}"
	if frappe.db.exists("Currency Exchange", {"from_currency": "USD", "to_currency": currency}):
		return log.note(False, "Currency Exchange", label)
	frappe.get_doc({
		"doctype": "Currency Exchange",
		"date": nowdate(),
		"from_currency": "USD",
		"to_currency": currency,
		"exchange_rate": USD_RATE,
		"for_buying": 1,
		"for_selling": 1,
	}).insert(ignore_permissions=True)
	return log.note(True, "Currency Exchange", label)


def ensure_tree_group(log, doctype, name_field, name, parent_field, parent):
	if frappe.db.exists(doctype, name):
		return log.note(False, doctype, name)
	frappe.get_doc({"doctype": doctype, name_field: name, parent_field: parent, "is_group": 0}).insert(
		ignore_permissions=True
	)
	return log.note(True, doctype, name)


def ensure_parties(log):
	ensure_tree_group(log, "Supplier Group", "supplier_group_name", SUPPLIER_GROUP,
		"parent_supplier_group", "All Supplier Groups")
	if frappe.db.exists("Supplier", {"supplier_name": SUPPLIER}):
		log.note(False, "Supplier", SUPPLIER)
	else:
		frappe.get_doc({
			"doctype": "Supplier",
			"supplier_name": SUPPLIER,
			"supplier_group": SUPPLIER_GROUP,
			"supplier_type": "Individual",
		}).insert(ignore_permissions=True)
		log.note(True, "Supplier", SUPPLIER)

	has_price_list = frappe.get_meta("Customer").has_field("default_price_list")
	for customer, group, price_list in CUSTOMERS:
		ensure_tree_group(log, "Customer Group", "customer_group_name", group,
			"parent_customer_group", "All Customer Groups")
		if frappe.db.exists("Customer", {"customer_name": customer}):
			log.note(False, "Customer", customer)
			continue
		doc = {"doctype": "Customer", "customer_name": customer, "customer_group": group, "customer_type": "Company"}
		if has_price_list:
			doc["default_price_list"] = price_list
		frappe.get_doc(doc).insert(ignore_permissions=True)
		log.note(True, "Customer", customer)
