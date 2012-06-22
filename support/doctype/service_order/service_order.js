cur_frm.cscript.tname = "Service Order Detail";
cur_frm.cscript.fname = "service_order_details";
cur_frm.cscript.other_fname = "other_charges";
cur_frm.cscript.sales_team_fname = "sales_team";

$import(Sales Common)
$import(Other Charges)

// --------
// onload
// --------
cur_frm.cscript.onload = function(doc, cdt, cdn) {
  if(!doc.status) set_multiple(cdt,cdn,{status:'Open'});
  if(!doc.transaction_date) set_multiple(cdt,cdn,{transaction_date:get_today()});
  if(!doc.conversion_rate) set_multiple(cdt,cdn,{conversion_rate:'1.00'});
  if(!doc.currency && sys_defaults.currency) set_multiple(cdt,cdn,{currency:sys_defaults.currency});
  if(!doc.company && sys_defaults.company) set_multiple(cdt,cdn,{company:sys_defaults.company});
  if(!doc.fiscal_year && sys_defaults.fiscal_year) set_multiple(cdt,cdn,{fiscal_year:sys_defaults.fiscal_year});
  if (!doc.note) doc.note = 'ACCEPTED AND CONFIRMED' + NEWLINE + NEWLINE + NEWLINE + NEWLINE + 'Signed and Date';
}


// --------
// refresh
// --------
cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  if(!doc.status) doc.status = 'Open';

  if(doc.quotation_type == 'Others') unhide_field('others_detail');
  else hide_field('others_detail');

  if (!doc.docstatus) hide_field(['Send SMS', 'message', 'customer_mobile_no']);
  else unhide_field(['Send SMS', 'message', 'customer_mobile_no']);
}

//customer
cur_frm.cscript.customer = function(doc,dt,dn) {
  var callback = function(r,rt) {
      var doc = locals[cur_frm.doctype][cur_frm.docname];
      cur_frm.refresh();
  }

  if(doc.customer) $c_obj(make_doclist(doc.doctype, doc.name), 'get_default_customer_address', '', callback);
  if(doc.customer) unhide_field(['customer_address','contact_person','customer_name','address_display','contact_display','contact_mobile','contact_email', 'contact_department', 'contact_designation', 'territory','customer_group', 'zone']);
}

cur_frm.cscript.customer_address = cur_frm.cscript.contact_person = function(doc,dt,dn) {
  if(doc.customer) get_server_fields('get_customer_address', JSON.stringify({customer: doc.customer, address: doc.customer_address, contact: doc.contact_person}),'', doc, dt, dn, 1);
}

cur_frm.fields_dict.customer_address.on_new = function(dn) {
  locals['Address'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
  locals['Address'][dn].customer_name = locals[cur_frm.doctype][cur_frm.docname].customer_name;
}

cur_frm.fields_dict.contact_person.on_new = function(dn) {
  locals['Contact'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
  locals['Contact'][dn].customer_name = locals[cur_frm.doctype][cur_frm.docname].customer_name;
}

cur_frm.fields_dict['customer_address'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,address_line1,city FROM tabAddress WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}


// ---------------
// contact person
// ---------------
cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}


// ------------------
// service quotation
// ------------------
cur_frm.fields_dict['service_quotation_no'].get_query = function(doc) {
  return 'SELECT DISTINCT `tabService Quotation`.`name` FROM `tabService Quotation` WHERE `tabService Quotation`.company = "' + doc.company + '" and `tabService Quotation`.`docstatus` = 1 and `tabService Quotation`.`status` != "Closed" and `tabService Quotation`.`name` like "%s" ORDER BY `tabService Quotation`.`name` DESC LIMIT 50';
}


// ------------------
// serial no details
// ------------------
cur_frm.cscript.serial_no = function(doc, cdt, cdn) {
  var d = locals[cdt][cdn];
  get_server_fields('get_serial_details', d.serial_no,'service_order_details',doc, cdt, cdn, 1);
}


// -----------------
// set qty and rate
// -----------------
cur_frm.cscript.amount = function(doc, cdt, cdn) {
  var d = locals[cdt][cdn];
  ret = {'qty':1, 'basic_rate':d.amount};
  set_multiple('Service Order Detail', d.name, ret, 'service_order_details');
  cur_frm.cscript.recalc(doc, 4);
}


// -----------
// order type
// -----------
cur_frm.cscript.order_type = function(doc,cdt,cdn) {
  if (doc.order_type == 'Others') unhide_field('others_detail');
  else hide_field('others_detail');
}


// ---------
// validate
// ---------
cur_frm.cscript.validate = function(doc,cdt,cdn) {
  if (doc.order_type == 'Others' && ! doc.others_detail) {
    validated = false;
    alert("Please enter 'Others Detail'");
  }
}
