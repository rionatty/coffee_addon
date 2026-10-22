# Copyright (c) 2026, CyveTech and contributors
# For license information, please see license.txt

"""The Goods Received Note, kept on ERPNext's Purchase Receipt.

The paper note is added up in a fixed order, and so is this:

	weight note rows        ->  bags and total kgs   (when there are rows)
	total kgs - less bags   =   sub gross kgs
	sub gross - reductions  =   net weight kgs
	net weight x price      =   total amount, and the amount in words

and the yields add up to the total yield. The reductions are entered in
kilos by the quality controller; nothing works them out.

The note is the receipt. When it has a net weight and the receipt has a
single item line, that line takes the net weight as its quantity and the
price paid as its rate, so the store and the supplier get the figures the
note shows. A receipt with several lines is left alone: the note cannot
say which of them it weighed.

Runs before ERPNext validates the receipt (hooks.py), so ERPNext's own
totals and taxes are worked out from these figures.
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, money_in_words

YIELD_FIELDS = ("custom_yield_sc18", "custom_yield_sc15", "custom_yield_sc12", "custom_yield_1199")


def before_validate(doc, method=None):
	add_up_weight_note(doc)
	set_total_yield(doc)
	apply_to_item(doc)


def add_up_weight_note(doc):
	rows = doc.get("custom_weight_note") or []
	if rows:
		doc.custom_bags = sum(cint(row.no_of_bags) for row in rows)
		doc.custom_total_kgs = sum(flt(row.kgs) for row in rows)

	total = flt(doc.get("custom_total_kgs"))
	less_bags = flt(doc.get("custom_less_bags_kgs"))
	reductions = flt(doc.get("custom_nett_reductions_kgs"))

	if less_bags > total:
		frappe.throw(
			_("Less Bags ({0} kgs) cannot be more than the Total ({1} kgs).").format(less_bags, total),
			title=_("Goods Received Note"),
		)
	sub_gross = total - less_bags
	if reductions > sub_gross:
		frappe.throw(
			_("Nett Reductions ({0} kgs) cannot be more than the Sub Gross ({1} kgs).").format(
				reductions, sub_gross
			),
			title=_("Goods Received Note"),
		)

	net_weight = sub_gross - reductions
	amount = flt(net_weight * flt(doc.get("custom_price_paid")), doc.precision("custom_total_amount"))

	doc.custom_sub_gross_kgs = sub_gross
	doc.custom_net_weight_kgs = net_weight
	doc.custom_total_amount = amount
	doc.custom_amount_in_words = money_in_words(amount, doc.get("currency")) if amount else ""


def set_total_yield(doc):
	doc.custom_yield_total = sum(flt(doc.get(fieldname)) for fieldname in YIELD_FIELDS)


def apply_to_item(doc):
	net_weight = flt(doc.get("custom_net_weight_kgs"))
	if not net_weight:
		return

	items = doc.get("items") or []
	if len(items) != 1:
		return

	row = items[0]
	row.qty = net_weight
	# ERPNext refuses a line whose received quantity is not accepted +
	# rejected (buying_controller.validate_accepted_rejected_qty).
	row.received_qty = net_weight + flt(row.rejected_qty)

	price = flt(doc.get("custom_price_paid"))
	if price:
		row.rate = price
