// --------------------
// get customer details
// ---------------------
cur_frm.cscript.customer = function(doc,dt,dn) {
  var callback = function(r,rt) {
      var doc = locals[cur_frm.doctype][cur_frm.docname];
      cur_frm.refresh();
  }

  if(doc.customer) $c_obj(make_doclist(doc.doctype, doc.name), 'get_default_customer_address', '', callback);
}

cur_frm.cscript.customer_address = cur_frm.cscript.contact_person = function(doc,dt,dn) {
  if(doc.customer) get_server_fields('get_customer_address', JSON.stringify({customer: doc.customer, address: doc.customer_address, contact: doc.contact_person}),'', doc, dt, dn, 1); 
}

cur_frm.fields_dict.customer_address.on_new = function(dn) {
  locals['Address'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
}

cur_frm.fields_dict.contact_person.on_new = function(dn) {
  locals['Contact'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
}

cur_frm.fields_dict['customer_address'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,address_line1,city FROM tabAddress WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}


// -----------------------
// get serial no details
// -----------------------
cur_frm.add_fetch('serial_no', 'brand', 'brand');
cur_frm.add_fetch('serial_no', 'product_code', 'order_reference_code');
