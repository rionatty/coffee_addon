# Copyright (c) 2026, CyveTech and contributors
# For license information, please see license.txt

"""The coffee demo's books, from the same files a person would import by hand:

	bench --site SITE execute coffee_addon.coffee_addon.demo_setup.run

It hands demo_import/ to ERPNext's own importers: the client's chart of
accounts to the Chart of Accounts Importer, then every master file to Data
Import, in the order demo_import/import_order.csv gives. So the books built
here and the books built through the desk cannot differ, and nothing is
written that the importers would not have written themselves.

What the files build (see demo_import/README.txt):
	* raw material apart from finished product, in the chart, the stores and
	  the item groups; finished product by coffee type (Robusta, Arabica),
	  then by screen, each screen its own Stock, Sales and Cost of Sales ledger;
	* item groups carrying each line's store and ledgers;
	* quality inspection parameters and templates, with every item on its
	  template, and the export grades needing an inspection (printed as the
	  Certificate of Analysis) before delivery;
	* export customers billed in USD to a USD receivable, local ones in UGX.

The files name the company's ledgers "NUMBER - Name - ICL", so they are for
Ideal Commodities (U) Ltd with abbreviation ICL, on a company with no
transactions yet (ERPNext only replaces a chart before any are posted).
Run it once: run again, each record already there is reported as a failed
row by Data Import and left as it is.
"""

import csv
import os

import frappe
from frappe import _

COMPANY = "Ideal Commodities (U) Ltd"
ABBR = "ICL"
CHART = "00_chart_of_accounts.xlsx"
ORDER = "import_order.csv"
# a ledger only the client's chart has: if it is there, the chart is in
CHART_MARKER = "12010311 - Robusta Screen 18 Stock - ICL"


def folder():
	return os.path.normpath(os.path.join(frappe.get_app_path("coffee_addon"), "..", "demo_import"))


def check_company(company):
	if company != COMPANY or not frappe.db.exists("Company", company):
		frappe.throw(_("The demo files are made for the company {0}.").format(frappe.bold(COMPANY)), title=_("Coffee demo"))
	if frappe.get_cached_value("Company", company, "abbr") != ABBR:
		frappe.throw(
			_("The demo files name every ledger '... - {0}': set {1}'s abbreviation to {0} first.").format(ABBR, company),
			title=_("Coffee demo"),
		)


def run(company=COMPANY, chart=True):
	check_company(company)

	if chart:
		import_chart(company)

	done = []
	with open(os.path.join(folder(), ORDER), encoding="utf-8") as f:
		for step in csv.DictReader(f):
			import_type = "update" if step["import_type"] == "Update Existing Records" else "insert"
			submit = (step.get("submit") or "").strip() == "1"
			import_master(step["doctype"], os.path.join(folder(), step["file"]), import_type, submit)
			done.append(step["file"])

	frappe.db.commit()
	print(f"Coffee demo for {company}: chart {'imported' if chart else 'left as it is'}; imported {', '.join(done)}.")
	print("Rows Data Import could not take are listed in its Import Log, one Data Import per file.")
	return done


def import_chart(company):
	"""The client's chart through ERPNext's Chart of Accounts Importer, once."""
	if frappe.db.exists("Account", CHART_MARKER):
		print("Chart of accounts already imported; leaving it as it is.")
		return

	from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import import_coa

	with open(os.path.join(folder(), CHART), "rb") as f:
		content = f.read()
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": CHART,
		"is_private": 1,
		"content": content,
	}).insert(ignore_permissions=True)
	import_coa(file_doc.file_url, company)
	print(f"Chart of accounts imported from {CHART}.")


def import_master(doctype, path, import_type, submit=False):
	from frappe.core.doctype.data_import.data_import import import_file

	print(f"Importing {os.path.basename(path)} ({doctype}, {import_type}{', submitted' if submit else ''}) ...")
	import_file(doctype, path, import_type, submit_after_import=submit, console=True)


# ─── Item groups, put right whatever an earlier import left ──────────────────
RAW_MATERIAL = "Raw Material"  # ERPNext's own group (a leaf from the setup wizard), made a group
RETIRED_GROUPS = ("Raw Coffee",)  # an earlier name for Raw Material in these files
GROUP_DEFAULTS = (
	"default_warehouse",
	"default_inventory_account",
	"income_account",
	"default_cogs_account",
	"expense_account",
)


def item_groups(company=COMPANY):
	"""Put the coffee item groups right, whatever earlier imports left on the site:

		bench --site SITE execute coffee_addon.coffee_addon.demo_setup.item_groups

	The tree it leaves is the one the demo files describe -
		Raw Material > Raw Robusta, Raw Arabica
		Finished Product > Robusta Grades > Robusta Grade 18 / 15 / 12 / Undergrades,
		                   Arabica Grades > Arabica Grade 18 / 15 / 12 / Undergrades,
		                   By-products
	- read from the same 03_item_group files Data Import uses. Groups that are
	missing are made, groups under the wrong parent are moved with everything
	under them, ERPNext's own "Raw Material" is made a group, and every group
	that holds stock gets its store and its Stock, Revenue and Cost of Sales
	ledgers for the company. The raw coffee ledgers (01b) are added first when
	the site lacks them. Other groups on the site are left as they are. Running
	it again changes nothing.
	"""
	check_company(company)
	add_missing_ledgers(company)

	rows = item_group_rows()
	stores = sorted({r["default_warehouse"] for r in rows if r.get("default_warehouse")})
	missing = [s for s in stores if not frappe.db.exists("Warehouse", s)]
	if missing:
		frappe.throw(
			_("Import the 02_warehouse files first. These stores are not on the site: {0}").format(", ".join(missing)),
			title=_("Coffee demo"),
		)

	report = []
	for row in rows:
		report.extend(put_item_group(row, company))
	report.extend(retire_groups())

	frappe.db.commit()
	for line in report or ["Item groups already right; nothing changed."]:
		print(line)
	return report


def item_group_rows():
	"""The tree, parents first: Raw Material, then the 03_item_group files in import order."""
	rows = [{"item_group_name": RAW_MATERIAL, "parent_item_group": "All Item Groups", "is_group": "1"}]
	with open(os.path.join(folder(), ORDER), encoding="utf-8") as f:
		files = [s["file"] for s in csv.DictReader(f) if s["doctype"] == "Item Group" and s["import_type"] == "Insert New Records"]
	for name in files:
		with open(os.path.join(folder(), name), encoding="utf-8") as f:
			for r in csv.DictReader(f):
				rows.append({
					"item_group_name": r["item_group_name"].strip(),
					"parent_item_group": r["parent_item_group"].strip(),
					"is_group": r["is_group"].strip(),
					**{k: (r.get("item_group_defaults." + k) or "").strip() for k in GROUP_DEFAULTS},
				})
	return rows


def put_item_group(row, company):
	name, parent, is_group = row["item_group_name"], row["parent_item_group"], frappe.utils.cint(row["is_group"])
	new = not frappe.db.exists("Item Group", name)
	doc = frappe.new_doc("Item Group") if new else frappe.get_doc("Item Group", name)
	if new:
		doc.item_group_name = name
	changes = []

	if doc.parent_item_group != parent:
		if not new:
			changes.append(f"moved from {doc.parent_item_group or '(top)'} to {parent}")
		doc.parent_item_group = parent
	if frappe.utils.cint(doc.is_group) != is_group:
		if not new:
			changes.append("made a group" if is_group else "made a leaf")
		doc.is_group = is_group

	if not is_group:
		meta = frappe.get_meta("Item Default")
		wanted = {k: row.get(k) for k in GROUP_DEFAULTS if row.get(k) and meta.has_field(k)}
		line = next((d for d in doc.get("item_group_defaults") or [] if d.company == company), None)
		if wanted and line is None:
			line = doc.append("item_group_defaults", {"company": company})
		for field, value in wanted.items():
			if line.get(field) != value:
				line.set(field, value)
				if not new:
					changes.append(f"{meta.get_label(field)} {value}")

	if not new and not changes:
		return []
	doc.flags.ignore_permissions = True
	doc.save()
	return [f"Item Group {name}: made under {parent}"] if new else [f"Item Group {name}: " + "; ".join(changes)]


def retire_groups():
	report = []
	for name in RETIRED_GROUPS:
		if not frappe.db.exists("Item Group", name):
			continue
		if frappe.db.exists("Item Group", {"parent_item_group": name}) or frappe.db.exists("Item", {"item_group": name}):
			report.append(f"Item Group {name}: left, it still has groups or items under it")
			continue
		frappe.delete_doc("Item Group", name, ignore_permissions=True)
		report.append(f"Item Group {name}: removed, its groups now sit under {RAW_MATERIAL}")
	return report


def add_missing_ledgers(company):
	"""The ledgers 01b_account_insert.csv adds, when the site does not have them yet."""
	with open(os.path.join(folder(), "01b_account_insert.csv"), encoding="utf-8") as f:
		for r in csv.DictReader(f):
			name = f"{r['account_number']} - {r['account_name']} - {ABBR}"
			if frappe.db.exists("Account", name):
				continue
			if not frappe.db.exists("Account", r["parent_account"]):
				frappe.throw(
					_("Import the client's chart of accounts first: {0} is not on the site.").format(r["parent_account"]),
					title=_("Coffee demo"),
				)
			frappe.get_doc({
				"doctype": "Account",
				"account_name": r["account_name"],
				"account_number": r["account_number"],
				"parent_account": r["parent_account"],
				"company": company,
				"is_group": 0,
				"account_type": r["account_type"],
			}).insert(ignore_permissions=True)
			print(f"Account {name}: added")
