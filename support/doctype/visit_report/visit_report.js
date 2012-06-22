// -------
// onload
// -------
cur_frm.cscript.onload = function(doc, cdt, cdn) {
  if(!doc.status) doc.status = 'Open';
}


// -------------
// item details
// -------------
cur_frm.add_fetch('item_code', 'brand', 'brand');
cur_frm.add_fetch('item_code', 'product_code', 'product_code');


// ------------------
// get owner details
// ------------------
cur_frm.add_fetch('prepared_by', 'territory', 'territory');
cur_frm.add_fetch('prepared_by', 'department', 'department');
cur_frm.add_fetch('prepared_by', 'designation', 'designation');


// ---------------------
// get customer details
// ---------------------
cur_frm.add_fetch('customer', 'territory', 'territory');


// ---------------------------
// get contact person details
// ---------------------------
cur_frm.fields_dict['visit_report_details'].grid.get_field("contact_person").get_query = function(doc, cdt, cdn) {
  var d = locals[this.doctype][this.docname];
  return 'SELECT name,CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE customer = "'+ d.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.add_fetch('contact_person', 'first_name', 'contact_name');
cur_frm.add_fetch('contact_person', 'department', 'department');
cur_frm.add_fetch('contact_person', 'designation', 'designation');


cur_frm.fields_dict['visit_report_details'].grid.get_field("against_document_no").get_query = function(doc, cdt, cdn){
  var d = locals[this.doctype][this.docname];
  if(d.against_document == 'Lead'){
    return 'SELECT `tab'+d.against_document+'`.`name` FROM `tab'+d.against_document+'` WHERE `tab'+d.against_document+'`.`name` LIKE "%s" ORDER BY `tab'+d.against_document+'`.`name` DESC LIMIT 50'
  }

  else if(d.against_document != 'Others'){
    return 'SELECT `tab'+d.against_document+' Report`.`name` FROM `tab'+d.against_document+' Report` WHERE `tab'+d.against_document+' Report`.`name` LIKE "%s" ORDER BY `tab'+d.against_document+' Report`.`name` DESC LIMIT 50'
  }

}
