cur_frm.cscript.service_person_name = function(doc, cdt, cdn) {
  var callback = function(r, rt){
    cur_frm.refresh();
  }
  var d = locals[cdt][cdn];
  if(d.service_person_name)  get_server_fields('get_service_person_details',d.service_person_name,'service_team',doc, cdt, cdn, 1, callback);
}

// ----------------------
// delivery note details
// ----------------------
cur_frm.fields_dict['delivery_note_no'].get_query = function(doc, cdt, cdn) {
  if(doc.customer_name){
    return 'SELECT DISTINCT `tabDelivery Note`.name,`tabDelivery Note`.customer_name FROM `tabDelivery Note` WHERE `tabDelivery Note`.docstatus = 1 AND `tabDelivery Note`.status != "Closed" AND `tabDelivery Note`.customer = "'+doc.customer+'" AND `tabDelivery Note`.`name` LIKE "%s" ORDER BY `tabDelivery Note`.`name` LIMIT 50'
  }
  else{
    return 'SELECT DISTINCT `tabDelivery Note`.name,`tabDelivery Note`.customer_name FROM `tabDelivery Note` WHERE `tabDelivery Note`.docstatus = 1 AND `tabDelivery Note`.status != "Closed" AND `tabDelivery Note`.`name` LIKE "%s" ORDER BY `tabDelivery Note`.`name` LIMIT 50'
  }
}

cur_frm.add_fetch('delivery_note_no', 'installation_date', 'scheduled_date');
cur_frm.add_fetch('delivery_note_no', 'customer', 'customer');
cur_frm.add_fetch('delivery_note_no', 'customer_name', 'customer_name');
cur_frm.add_fetch('delivery_note_no', 'customer_address', 'customer_address');
cur_frm.add_fetch('delivery_note_no', 'delivery_address', 'address');
cur_frm.add_fetch('delivery_note_no', 'contact_person', 'contact_person');
cur_frm.add_fetch('delivery_note_no', 'contact_display', 'contact_name');
cur_frm.add_fetch('delivery_note_no', 'contact_department', 'department');
cur_frm.add_fetch('delivery_note_no', 'contact_designation', 'designation');


// ----------------------
// get serial no details
// ----------------------
cur_frm.add_fetch('serial_no', 'brand', 'brand');
cur_frm.add_fetch('serial_no', 'product_code', 'other_reference_code');
cur_frm.add_fetch('serial_no', 'software_version', 'version');
cur_frm.add_fetch('serial_no', 'item_code', 'catalogue_code');
cur_frm.add_fetch('serial_no', 'warranty_expiry_date', 'warranty_expiry_date');


// ----------------------
// get customer details
// ----------------------
cur_frm.add_fetch('customer', 'customer_name', 'customer_name');
cur_frm.add_fetch('customer', 'territory', 'territory');

cur_frm.cscript.customer = function(doc, dt, dn) {
  if(doc.customer){
      var callback = function(r, rt){
         var doc = locals[cur_frm.doctype][cur_frm.docname];
         cur_frm.refresh();
      }
      $c_obj(make_doclist(doc.doctype, doc.name), 'get_customer_details', '',callback);
  }
}


cur_frm.cscript.contact_person = function(doc, cdt, cdn) {
  get_server_fields('get_contact_details','','', doc, cdt, cdn, 1);
}

cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
  return 'SELECT `tabContact`.contact_name FROM `tabContact` WHERE `tabContact`.is_customer = 1 AND `tabContact`.customer_name = "'+ doc.customer_name+'" AND `tabContact`.contact_name LIKE "%s" ORDER BY `tabContact`.name ASC LIMIT 50';
}
