// Module CRM
cur_frm.cscript.tname = "MIS Item Detail";
cur_frm.cscript.fname = "mis_item_details";

$import(Item Common)

// ------------------------
// PO Receipt Date Trigger
// ------------------------
cur_frm.cscript.po_receipt_date = function(doc, dt, dn){
	if(doc.po_receipt_date){
		dt = wn.datetime.str_to_obj(doc.po_receipt_date);
		year = dt.getFullYear();
		month = dt.getMonth();
		var month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
		doc.po_receipt_month = month_list[month];
		if(month < 3){
			doc.po_receipt_fiscal_year = cstr(year-1)+'-'+cstr(year);
		}
		else{
			doc.po_receipt_fiscal_year = cstr(year)+'-'+cstr(year+1);
		}
		refresh_many(['po_receipt_month', 'po_receipt_fiscal_year']);
	}
}


// ---------------
// Execution Date
// ---------------
cur_frm.cscript.execution_date = function(doc, dt, dn){
	if(doc.execution_date){
		dt = wn.datetime.str_to_obj(doc.execution_date);
		year = dt.getFullYear();
		month = dt.getMonth();
		var qtr_list = ['Q4','Q4','Q4','Q1','Q1','Q1','Q2','Q2','Q2','Q3','Q3','Q3'];
		doc.execution_quarter = qtr_list[month];
		if(month < 3){
			doc.execution_fiscal_year = cstr(year-1)+'-'+cstr(year);
		}
		else{
			doc.execution_fiscal_year = cstr(year)+'-'+cstr(year+1);
		}
		refresh_many(['execution_quarter', 'execution_fiscal_year']);
	}

}


// ----------------------
// Get Customer Details
// ---------------------
cur_frm.add_fetch('customer', 'territory', 'territory');


// --------------------
// Fetch Item Details
// --------------------
cur_frm.add_fetch('item_code', 'product_code', 'order_ref_code');
cur_frm.add_fetch('item_code', 'brand', 'brand');
cur_frm.add_fetch('item_code', 'description', 'description');
cur_frm.add_fetch('item_code', 'item_type', 'item_type');



cur_frm.cscript.ref_rate_inr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	if(d.ref_rate_inr){
		d.discount_value_inr = flt(d.ref_rate_inr) - flt(d.po_value_inr);
		d.discount_percent = (flt(d.ref_rate_inr) - flt(d.po_value_inr)) * 100 / flt(d.ref_rate_inr);
		refresh_field('discount_value_inr', d.name, 'mis_item_details');
		refresh_field('discount_percent', d.name, 'mis_item_details');
	}
	cur_frm.cscript.calculate_balance_amount(doc, cdt, cdn);
}



// ------------------
// PO Value FCNR INR
// ------------------
cur_frm.cscript.po_value_fcnr_inr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	if(d.po_value_fcnr_inr){
		d.po_value_inr = flt(d.po_value_fcnr_inr) * flt(doc.factor_figure_rate);
		d.po_value_in_lakhs_inr = flt(d.po_value_inr)/100000;
		d.discount_value_inr = flt(d.ref_rate_inr) - flt(d.po_value_inr);
		d.discount_percent = (flt(d.ref_rate_inr) - flt(d.po_value_inr)) * 100 / flt(d.ref_rate_inr);
		refresh_field('po_value_in_lakhs_inr', d.name, 'mis_item_details');
		refresh_field('discount_value_inr', d.name, 'mis_item_details');
		refresh_field('discount_percent', d.name, 'mis_item_details');
		refresh_field('po_value_inr', d.name, 'mis_item_details');
	}
	cur_frm.cscript.calculate_balance_amount(doc, cdt, cdn);
}



// --------------
// PO value INR
// --------------
cur_frm.cscript.po_value_inr = function(doc, dt, dn){
	var d = locals[dt][dn];
	if(d.po_value_inr){
		d.po_value_in_lakhs_inr = flt(d.po_value_inr)/100000;
		d.discount_value_inr = flt(d.ref_rate_inr) - flt(d.po_value_inr);
		d.discount_percent = (flt(d.ref_rate_inr) - flt(d.po_value_inr)) * 100 / flt(d.ref_rate_inr);
		if(doc.factor_figure_rate){
			d.po_value_fcnr_inr = flt(d.po_value_inr) / flt(doc.factor_figure_rate);
			refresh_field('po_value_fcnr_inr', d.name, 'mis_item_details');
		}
		refresh_field('po_value_in_lakhs_inr', d.name, 'mis_item_details');
		refresh_field('discount_value_inr', d.name, 'mis_item_details');
		refresh_field('discount_percent', d.name, 'mis_item_details');
	}
	cur_frm.cscript.calculate_balance_amount(doc, cdt, cdn);
}


cur_frm.cscript.amount_received = function(doc, dt, dn){
	cur_frm.cscript.calculate_balance_amount(doc, cdt, cdn);
}

cur_frm.cscript.calculate_balance_amount = function(doc, dt, dn){
	var cl = getchildren('MIS Item Detail', doc.name, 'mis_item_details');
	var balance_amount = 0
	for(var i=0; i<cl.length; i++){
		balance_amount += flt(cl[i].po_value_inr);
	}
	doc.amount_balance = balance_amount - flt(doc.amount_received);
	refresh_field('amount_balance');
}

cur_frm.cscript['Re-Calculate Values'] = function(doc, cdt, cdn) {
	var tname = 'MIS Item Detail';
	var fname = 'mis_item_details';
	var cl = getchildren(tname, doc.name, fname);
	var balance_amount = 0;
	for(var i=0; i<cl.length; i++){
		if(cl[i].po_value_inr){
			if(doc.factor_figure_rate){
				set_multiple(tname, cl[i].name, {'po_value_fcnr_inr':flt(cl[i].po_value_inr) / flt(doc.factor_figure_rate)}, fname);
			}
			set_multiple(tname, cl[i].name, {'po_value_in_lakhs_inr': flt(cl[i].po_value_inr)/100000, 'discount_value_inr': flt(cl[i].ref_rate_inr) - flt(cl[i].po_value_inr), 'discount_percent': (flt(cl[i].ref_rate_inr) - flt(cl[i].po_value_inr)) * 100 / flt(cl[i].ref_rate_inr)}, fname);
		}
		else if(cl[i].po_value_fcnr_inr){
			set_multiple(tname, cl[i].name, {'po_value_inr': flt(cl[i].po_value_fcnr_inr) * flt(doc.factor_figure_rate)}, fname);
			set_multiple(tname, cl[i].name, {'po_value_in_lakhs_inr': flt(cl[i].po_value_inr) / 100000, 'discount_value_inr': flt(cl[i].ref_rate_inr) - flt(cl[i].po_value_inr), 'discount_percent': (flt(cl[i].ref_rate_inr)-flt(cl[i].po_value_inr))*100/flt(cl[i].ref_rate_inr)}, fname);
		}
		balance_amount += flt(cl[i].po_value_inr);
	}
	doc.amount_balance = balance_amount - flt(doc.amount_received);
	refresh_field('amount_balance');
}

cur_frm.cscript.validate = function(doc, cdt, cdn){
	cur_frm.cscript['Re-Calculate Values'](doc, cdt, cdn);
}
