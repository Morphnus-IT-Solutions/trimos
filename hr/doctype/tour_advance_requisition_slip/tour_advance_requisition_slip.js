// -------
// refresh
// --------
cur_frm.cscript.refresh = function(doc, cdt, cdn){

  cur_frm.clear_custom_buttons();
 
  if(!doc.__islocal) cur_frm.add_custom_button('Send for Approval', cur_frm.cscript['Send for Approval']);
  
  if(inList(user_roles, 'Accounts Team') && !doc.__islocal) {
    unhide_field(['bills_received_on','allowed_status']);
    cur_frm.add_custom_button('Send Feedback', cur_frm.cscript['Send Feedback']);  }
  else {
    hide_field(['bills_received_on','allowed_status']);
  }
}


// -----------------
// employee details
// -----------------
cur_frm.add_fetch('employee_name', 'department', 'department');
cur_frm.add_fetch('employee_name', 'designation', 'designation');
cur_frm.add_fetch('employee_name', 'territory', 'territory');


cur_frm.cscript.fare = function(doc){
  cur_frm.cscript.calc_total(doc);
}

cur_frm.cscript.hotel_expense = function(doc){
  cur_frm.cscript.calc_total(doc);
}

cur_frm.cscript.food_expense = function(doc){
  cur_frm.cscript.calc_total(doc);
}

cur_frm.cscript.conveyance = function(doc){
  cur_frm.cscript.calc_total(doc);
}

cur_frm.cscript.miscellaneous = function(doc){
  cur_frm.cscript.calc_total(doc);
}

cur_frm.cscript.calc_total = function(doc){
  doc.total = flt(doc.fare) + flt(doc.hotel_expense) + flt(doc.food_expense) + flt(doc.conveyance) + flt(doc.miscellaneous)
  refresh_field('total');
}

cur_frm.cscript.total = function(doc){
  if(doc.allowed_amount){
    doc.disallowed_amount = flt(doc.total) - flt(doc.allowed_amount);
    refresh_field('disallowed_amount');
  }  
}

cur_frm.cscript.allowed_amount = function(doc){
  if(doc.total){
    doc.disallowed_amount = flt(doc.total) - flt(doc.allowed_amount);
    refresh_field('disallowed_amount');
  }
}

cur_frm.cscript['Send for Approval'] = function() {
  var doc = cur_frm.doc;
  $c_obj(make_doclist(doc.doctype, doc.name),'send_for_approval','', function(){});
}

cur_frm.cscript['Send Feedback'] = function() {
  var doc = cur_frm.doc;
  $c_obj(make_doclist(doc.doctype, doc.name),'send_feedback','', function(){});
}
