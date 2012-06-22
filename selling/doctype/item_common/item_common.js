// ------------------------
// Get Factor Figure Rate
// ------------------------
cur_frm.add_fetch('factor_figure', 'factor_figure_rate', 'factor_figure_rate')

// -------------------
// Get Item Details
// -------------------
cur_frm.cscript.item_code = function(doc, cdt, cdn) {
  var fname = cur_frm.cscript.fname;
  var d = locals[cdt][cdn];
  if (d.item_code) {
      var callback = function(r, rt){
	refresh_field(fname);
      }
      get_server_fields('get_item_details', JSON.stringify({'item':d.item_code, 'qty':d.qty}), fname, doc, cdt, cdn, 1, callback);
    }
}


// -----------------
// Calculate Amount
// -----------------
cur_frm.cscript.calculate_amount = function(doc, cdt, cdn){
	$c_obj(make_doclist(doc.doctype,doc.name),'calculate_amount','', function(r, rt) { var fname = cur_frm.cscript.fname; refresh_field(fname);});
}


cur_frm.cscript.currency = function(doc, cdt, cdn){
	cur_frm.cscript.calculate_amount(doc, cdt, cdn);
}

cur_frm.cscript.price_list = function(doc, cdt, cdn){
	cur_frm.cscript.calculate_amount(doc, cdt, cdn);
}

cur_frm.cscript.factor_figure = function(doc, cdt, cdn){
	cur_frm.cscript.calculate_amount(doc, cdt, cdn);
}

cur_frm.cscript.factor_figure_rate = function(doc, cdt, cdn){
	if(flt(doc.factor_figure_rate) == 0) doc.factor_figure_rate = 1.00;
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;

	var cl = getchildren(tname, doc.name, fname);
	for(var i=0;i<cl.length;i++){
		set_multiple(tname, cl[i].name, {'ref_rate_inr': flt(cl[i].ref_rate_fcnr) * flt(doc.factor_figure_rate), 'amount_inr': flt(cl[i].ref_rate_fcnr) * flt(cl[i].qty) * flt(doc.factor_figure_rate)}, fname);
		refresh_many(['ref_rate_inr', 'amount_inr']);
	}
}

cur_frm.cscript.qty = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;
	set_multiple(tname, d.name, {'amount_inr': flt(d.ref_rate_inr) * flt(d.qty), 'amount_fcnr': flt(d.ref_rate_fcnr) * flt(d.qty)}, fname);
	refresh_many(['amount_inr', 'amount_fcnr']);
}

cur_frm.cscript.ref_rate_inr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;
	set_multiple(tname, d.name, {'ref_rate_fcnr': flt(d.ref_rate_inr) / flt(doc.factor_figure_rate), 'amount_inr': flt(d.ref_rate_inr) * flt(d.qty), 'amount_fcnr': flt(d.ref_rate_inr) * flt(d.qty) / flt(doc.factor_figure_rate)}, fname);
	refresh_many(['ref_rate_fcnr', 'amount_inr', 'amount_fcnr']);
}

cur_frm.cscript.ref_rate_fcnr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;
	set_multiple(tname, d.name, {'ref_rate_inr': flt(d.ref_rate_fcnr) * flt(doc.factor_figure_rate), 'amount_inr': flt(d.ref_rate_fcnr) * flt(d.qty) * flt(doc.factor_figure_rate), 'amount_fcnr': flt(d.ref_rate_fcnr) * flt(d.qty)}, fname);
	refresh_many(['ref_rate_inr', 'amount_inr', 'amount_fcnr']);
}

cur_frm.cscript.amount_fcnr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;
	set_multiple(tname, d.name, {'amount_inr': flt(d.amount_fcnr) * flt(doc.factor_figure_rate)}, fname);
	refresh_many(['amount_inr']);
}

cur_frm.cscript.amount_inr = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var fname = cur_frm.cscript.fname;
	var tname = cur_frm.cscript.tname;
	set_multiple(tname, d.name, {'amount_fcnr': flt(d.amount_inr) / flt(doc.factor_figure_rate)}, fname);
	refresh_many(['amount_fcnr']);
}
