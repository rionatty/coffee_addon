# Copyright (c) 2026, CyveTech and contributors
# For license information, please see license.txt

"""The coffee demo's masters, built in one command:

	bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run --kwargs "{'company': 'Your Company'}"

Coffee type is the group and the screens are ledgers under it, in stock,
sales and cost of sales alike:

	12010110 Robusta Stock                41010110 Robusta Sales
		12010111 Robusta FAQ Stock            41010111 Robusta Screen 18 Sales
		12010112 Robusta Screen 18 Stock      ...
		...
	12010120 Arabica Stock                41010120 Arabica Sales
		...                                   ...
	12010130 By-products Stock            41010130 By-product Sales

so the balance sheet and the P&L show Robusta and Arabica side by side, and
each screen within them. Each line has its own store posting to its Stock
ledger (under a Robusta Stores or Arabica Stores group), and its items carry
that store and their Sales and Cost of Sales ledgers as their defaults. The
item groups are by screen (Screen 18 holds Robusta Screen 18 and Arabica
Screen 18), so stock and sales can also be read across both types.

The same masters as demo_import/ (the client's chart of accounts and the
Data Import files). Run it after importing the chart to fill in the rest, or
on ERPNext's standard chart, where it also adds the coffee ledgers.

Prices and the USD rate are demo figures. Safe to run again: anything that
already exists, including defaults set in the desk, is left as it is.
"""

from collections import namedtuple

import frappe
from frappe import _
from frappe.utils import nowdate

Line = namedtuple("Line", "coffee_type item_group store stock sales cost items")

TYPES = {
	"Robusta": {"stock": ("12010110", "Robusta Stock"), "sales": ("41010110", "Robusta Sales"),
		"cost": ("51010110", "Robusta Cost of Sales"), "stores": "Robusta Stores"},
	"Arabica": {"stock": ("12010120", "Arabica Stock"), "sales": ("41010120", "Arabica Sales"),
		"cost": ("51010120", "Arabica Cost of Sales"), "stores": "Arabica Stores"},
}

LINES = (
	Line("Robusta", "Raw Coffee", "Robusta FAQ Store", ("12010111", "Robusta FAQ Stock"), None, None,
		("Robusta FAQ",)),
	Line("Robusta", "Screen 18", "Robusta Screen 18 Store", ("12010112", "Robusta Screen 18 Stock"),
		("41010111", "Robusta Screen 18 Sales"), ("51010111", "Robusta Screen 18 Cost of Sales"), ("Robusta Screen 18",)),
	Line("Robusta", "Screen 15", "Robusta Screen 15 Store", ("12010113", "Robusta Screen 15 Stock"),
		("41010112", "Robusta Screen 15 Sales"), ("51010112", "Robusta Screen 15 Cost of Sales"), ("Robusta Screen 15",)),
	Line("Robusta", "Screen 12", "Robusta Screen 12 Store", ("12010114", "Robusta Screen 12 Stock"),
		("41010113", "Robusta Screen 12 Sales"), ("51010113", "Robusta Screen 12 Cost of Sales"), ("Robusta Screen 12",)),
	# BHP 1199 is on the GRN's yields; rename the other undergrades to the
	# client's own names once they are confirmed.
	Line("Robusta", "Undergrades", "Robusta Undergrades Store", ("12010115", "Robusta Undergrades Stock"),
		("41010114", "Robusta Undergrade Sales"), ("51010114", "Robusta Undergrade Cost of Sales"),
		("Robusta BHP 1199", "Robusta Triage", "Robusta Blacks", "Robusta Browns", "Robusta Pods")),
	Line("Arabica", "Raw Coffee", "Arabica Parchment Store", ("12010121", "Arabica Parchment Stock"), None, None,
		("Arabica Parchment",)),
	Line("Arabica", "Screen 18", "Arabica Screen 18 Store", ("12010122", "Arabica Screen 18 Stock"),
		("41010121", "Arabica Screen 18 Sales"), ("51010121", "Arabica Screen 18 Cost of Sales"), ("Arabica Screen 18",)),
	Line("Arabica", "Screen 15", "Arabica Screen 15 Store", ("12010123", "Arabica Screen 15 Stock"),
		("41010122", "Arabica Screen 15 Sales"), ("51010122", "Arabica Screen 15 Cost of Sales"), ("Arabica Screen 15",)),
	Line("Arabica", "Screen 12", "Arabica Screen 12 Store", ("12010124", "Arabica Screen 12 Stock"),
		("41010123", "Arabica Screen 12 Sales"), ("51010123", "Arabica Screen 12 Cost of Sales"), ("Arabica Screen 12",)),
	Line("Arabica", "Undergrades", "Arabica Undergrades Store", ("12010125", "Arabica Undergrades Stock"),
		("41010124", "Arabica Undergrade Sales"), ("51010124", "Arabica Undergrade Cost of Sales"),
		("Arabica Triage", "Arabica Blacks", "Arabica Browns", "Arabica Pods")),
	# dust and husks come from both types
	Line(None, "By-products", "By-products Store", ("12010130", "By-products Stock"),
		("41010130", "By-product Sales"), ("51010130", "By-product Cost of Sales"), ("Coffee Dust", "Coffee Husks")),
)

ROOT_GROUP = "All Item Groups"
FINISHED_GOODS = "Finished Goods"
RAW_COFFEE_GROUP = "Raw Coffee"
ITEM_GROUPS = (  # (name, parent, is_group), parents first
	(FINISHED_GOODS, ROOT_GROUP, 1),
	(RAW_COFFEE_GROUP, ROOT_GROUP, 0),
	("Screen 18", FINISHED_GOODS, 0),
	("Screen 15", FINISHED_GOODS, 0),
	("Screen 12", FINISHED_GOODS, 0),
	("Undergrades", FINISHED_GOODS, 0),
	("By-products", ROOT_GROUP, 0),
)
UOM = "Kg"

BUYING_PRICE_LIST = "Standard Buying"
SELLING_PRICE_LIST = "Standard Selling"
EXPORT_PRICE_LIST = "Export (USD)"

# Demo figures. The Robusta buying price is the one paid on GRN 1731.
BUYING_PRICES = {"Robusta FAQ": 11800, "Arabica Parchment": 14500}
EXPORT_PRICES = {
	"Robusta Screen 18": 5.20, "Robusta Screen 15": 4.95, "Robusta Screen 12": 4.60,
	"Robusta BHP 1199": 3.10, "Robusta Triage": 2.60, "Robusta Blacks": 2.20, "Robusta Browns": 2.40, "Robusta Pods": 1.80,
	"Arabica Screen 18": 6.80, "Arabica Screen 15": 6.40, "Arabica Screen 12": 5.90,
	"Arabica Triage": 3.20, "Arabica Blacks": 2.60, "Arabica Browns": 2.80, "Arabica Pods": 2.10,
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
	parents = LedgerParents(company)

	ensure_uom(log)
	for name, parent, is_group in ITEM_GROUPS:
		ensure_item_group(log, name, parent, is_group)

	type_groups = {}
	for coffee_type, ledgers in TYPES.items():
		type_groups[coffee_type] = {
			"stock": ensure_account(log, company, ledgers["stock"], parents.stock, "Stock", is_group=1),
			"sales": ensure_account(log, company, ledgers["sales"], parents.income, None, is_group=1),
			"cost": ensure_account(log, company, ledgers["cost"], parents.cost, None, is_group=1),
			"stores": ensure_warehouse(log, company, ledgers["stores"], None, is_group=1),
		}

	for line in LINES:
		group = type_groups.get(line.coffee_type)
		stock = ensure_account(log, company, line.stock, (lambda g=group: g["stock"]) if group else parents.stock, "Stock")
		sales = line.sales and ensure_account(
			log, company, line.sales, (lambda g=group: g["sales"]) if group else parents.income, "Income Account")
		cost = line.cost and ensure_account(
			log, company, line.cost, (lambda g=group: g["cost"]) if group else parents.cost, "Cost of Goods Sold")
		store = ensure_warehouse(log, company, line.store, stock, parent=group["stores"] if group else None)
		defaults = {"company": company, "default_warehouse": store, "income_account": sales, "expense_account": cost}
		for item_code in line.items:
			ensure_item(log, item_code, line.item_group, defaults,
				sells=bool(line.sales), buys=line.item_group == RAW_COFFEE_GROUP)

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


class LedgerParents:
	"""Where new ledgers go: beside the company's own stock, sales and cost of
	goods sold ledgers. Looked up only when a ledger has to be created, so a
	company whose chart already has them (the client's imported chart) needs
	none of this."""

	def __init__(self, company):
		self.company = company
		self._found = {}

	def stock(self):
		return self._find("default_inventory_account", "Stock Assets")

	def income(self):
		return self._find("default_income_account", "Direct Income", "Income")

	def cost(self):
		return self._find("default_expense_account", "Stock Expenses", "Direct Expenses")

	def _find(self, company_field, *group_names):
		if company_field not in self._found:
			account = frappe.get_cached_value("Company", self.company, company_field)
			parent = account and frappe.db.get_value("Account", account, "parent_account")
			for account_name in group_names:
				if parent:
					break
				parent = frappe.db.get_value("Account", {"company": self.company, "is_group": 1, "account_name": account_name})
			if not parent:
				frappe.throw(
					_("{0} has no {1} account to put the coffee ledgers beside. Set it on the Company first.").format(
						self.company, group_names[0]
					),
					title=_("Coffee demo"),
				)
			self._found[company_field] = parent
		return self._found[company_field]


def ensure_uom(log):
	if frappe.db.exists("UOM", UOM):
		return log.note(False, "UOM", UOM)
	frappe.get_doc({"doctype": "UOM", "uom_name": UOM}).insert(ignore_permissions=True)
	return log.note(True, "UOM", UOM)


def ensure_account(log, company, number_name, parent, account_type, is_group=0):
	"""`parent` is called only when the ledger has to be created."""
	number, account_name = number_name
	existing = frappe.db.get_value("Account", {"company": company, "account_name": account_name})
	if existing:
		return log.note(False, "Account", existing)
	doc = frappe.get_doc({
		"doctype": "Account",
		"company": company,
		"account_name": account_name,
		"account_number": number,
		"parent_account": parent(),
		"is_group": is_group,
		"account_type": account_type,
	}).insert(ignore_permissions=True)
	return log.note(True, "Account", doc.name)


def ensure_warehouse(log, company, warehouse_name, account, is_group=0, parent=None):
	existing = frappe.db.get_value("Warehouse", {"company": company, "warehouse_name": warehouse_name})
	if existing:
		return log.note(False, "Warehouse", existing)
	if not parent:
		# the company's top store group ("All Warehouses"), not just any group
		groups = frappe.get_all(
			"Warehouse",
			filters={"company": company, "is_group": 1},
			fields=["name", "parent_warehouse"],
			order_by="lft asc",
		)
		parent = next((g.name for g in groups if not g.parent_warehouse), None)
	doc = frappe.get_doc({
		"doctype": "Warehouse",
		"warehouse_name": warehouse_name,
		"company": company,
		"parent_warehouse": parent,
		"is_group": is_group,
		"account": account,
	}).insert(ignore_permissions=True)
	return log.note(True, "Warehouse", doc.name)


def ensure_item_group(log, name, parent, is_group=0):
	if frappe.db.exists("Item Group", name):
		return log.note(False, "Item Group", name)
	frappe.get_doc({
		"doctype": "Item Group",
		"item_group_name": name,
		"parent_item_group": parent,
		"is_group": is_group,
	}).insert(ignore_permissions=True)
	return log.note(True, "Item Group", name)


def ensure_item(log, item_code, item_group, defaults, sells, buys):
	"""Each item carries its own store and ledgers, so Robusta Screen 18 and
	Arabica Screen 18 share the Screen 18 group yet post to their own
	ledgers. Defaults are only added for a company that has none on the item,
	so any set in the desk are never overwritten."""
	created = not frappe.db.exists("Item", item_code)
	if created:
		doc = frappe.get_doc({
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
		})
	else:
		doc = frappe.get_doc("Item", item_code)

	changed = False
	if not any(row.company == defaults["company"] for row in doc.get("item_defaults") or []):
		doc.append("item_defaults", {key: value for key, value in defaults.items() if value})
		changed = True

	if created:
		doc.insert(ignore_permissions=True)
	elif changed:
		doc.save(ignore_permissions=True)
	return log.note(created or changed, "Item", item_code)


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
		"uom": UOM,
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
