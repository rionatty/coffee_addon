// Coffee Addon — the Goods Received Note adds itself up as it is typed,
// in the order the paper note is added up:
//
//   weight note rows        ->  bags and total kgs (when there are rows)
//   total kgs - less bags   =   sub gross kgs
//   sub gross - reductions  =   net weight kgs
//   net weight x price      =   total amount
//
// and the yields add up to the total yield. The same sums run on the server
// when the receipt is saved (goods_received_note.py), which is also where
// the amount in words and the item line are filled in; the form only shows
// the figures while they are being typed.

(function () {
	const YIELD_FIELDS = ["custom_yield_sc18", "custom_yield_sc15", "custom_yield_sc12", "custom_yield_1199"];
	const INPUTS = ["custom_total_kgs", "custom_less_bags_kgs", "custom_nett_reductions_kgs", "custom_price_paid"];

	function set_if_changed(frm, fieldname, value) {
		if (flt(frm.doc[fieldname]) !== flt(value)) {
			frm.set_value(fieldname, value);
			return true;
		}
		return false;
	}

	function add_up(frm) {
		if (frm.doc.docstatus !== 0) return;

		const rows = frm.doc.custom_weight_note || [];
		if (rows.length) {
			set_if_changed(frm, "custom_bags", rows.reduce((sum, row) => sum + cint(row.no_of_bags), 0));
			set_if_changed(frm, "custom_total_kgs", rows.reduce((sum, row) => sum + flt(row.kgs), 0));
		}

		const sub_gross = flt(frm.doc.custom_total_kgs) - flt(frm.doc.custom_less_bags_kgs);
		const net_weight = sub_gross - flt(frm.doc.custom_nett_reductions_kgs);
		const amount = flt(net_weight * flt(frm.doc.custom_price_paid), precision("custom_total_amount"));

		set_if_changed(frm, "custom_sub_gross_kgs", sub_gross);
		set_if_changed(frm, "custom_net_weight_kgs", net_weight);
		if (set_if_changed(frm, "custom_total_amount", amount) && frm.doc.custom_amount_in_words) {
			// written out again from the new amount when the receipt is saved
			frm.set_value("custom_amount_in_words", "");
		}
	}

	function add_up_yields(frm) {
		if (frm.doc.docstatus !== 0) return;
		set_if_changed(frm, "custom_yield_total", YIELD_FIELDS.reduce((sum, f) => sum + flt(frm.doc[f]), 0));
	}

	const handlers = {};
	INPUTS.forEach((fieldname) => (handlers[fieldname] = add_up));
	YIELD_FIELDS.forEach((fieldname) => (handlers[fieldname] = add_up_yields));
	frappe.ui.form.on("Purchase Receipt", handlers);

	frappe.ui.form.on("Coffee Weight Note", {
		no_of_bags: add_up,
		kgs: add_up,
		custom_weight_note_remove: add_up,
	});
})();
