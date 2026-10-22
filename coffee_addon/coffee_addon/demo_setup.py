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


def run(company=COMPANY, chart=True):
	if company != COMPANY or not frappe.db.exists("Company", company):
		frappe.throw(_("The demo files are made for the company {0}.").format(frappe.bold(COMPANY)), title=_("Coffee demo"))
	if frappe.get_cached_value("Company", company, "abbr") != ABBR:
		frappe.throw(
			_("The demo files name every ledger '... - {0}': set {1}'s abbreviation to {0} first.").format(ABBR, company),
			title=_("Coffee demo"),
		)

	if chart:
		import_chart(company)

	done = []
	with open(os.path.join(folder(), ORDER), encoding="utf-8") as f:
		for step in csv.DictReader(f):
			import_type = "update" if step["import_type"] == "Update Existing Records" else "insert"
			import_master(step["doctype"], os.path.join(folder(), step["file"]), import_type)
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


def import_master(doctype, path, import_type):
	from frappe.core.doctype.data_import.data_import import import_file

	print(f"Importing {os.path.basename(path)} ({doctype}, {import_type}) ...")
	import_file(doctype, path, import_type, console=True)
