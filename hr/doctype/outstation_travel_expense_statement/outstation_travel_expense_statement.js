cur_frm.add_fetch('expense_limit', 'limit_amount', 'limit_amount');

cur_frm.cscript.refresh = function(doc, cdt, cdn){
  if(!doc.status)
    doc.status = 'Open';
  
  cur_frm.clear_custom_buttons();
 
  if(!doc.__islocal) cur_frm.add_custom_button('Send for Approval', cur_frm.cscript['Send for Approval']);
  
  if(inList(user_roles, 'Accounts Team') && !doc.__islocal) {
    unhide_field(['bills_received_on','allowed_status']);
    cur_frm.add_custom_button('Send Feedback', cur_frm.cscript['Send Feedback']);  }
  else {
    hide_field(['bills_received_on','allowed_status']);
  }

}  

cur_frm.add_fetch('employee_name', 'department', 'department');
cur_frm.add_fetch('employee_name', 'designation', 'designation');
cur_frm.add_fetch('employee_name', 'territory', 'territory');

cur_frm.cscript.allowed_expense = function(doc, cdt, cdn){
  var d = locals[cdt][cdn];
  if(d.allowed_expense){
    set_multiple('Travel Expense Details', d.name, { 'disallowed_expense': flt(d.expense) - flt(d.allowed_expense)}, 'travel_expense_details');
    refresh_field('disallowed_expense', d.name, 'travel_expense_details');
  }
}

cur_frm.cscript.expense = function(doc, cdt, cdn) {
  var d = locals[cdt][cdn];
  if(d.expense && d.allowed_expense) {
    set_multiple('Travel Expense Details', d.name, { 'disallowed_expense': flt(d.expense) - flt(d.allowed_expense)}, 'travel_expense_details');
    refresh_field('disallowed_expense', d.name, 'travel_expense_details');
  }
}

cur_frm.cscript.advance_id = function(doc, cdt, cdn){
  var callback = function(r, rt){
    refresh_field('less_adv_rec_from');
  }
  $c_obj(make_doclist(doc.doctype, doc.name), 'get_advance', '', callback);
}

cur_frm.cscript['Send for Approval'] = function() {
  var doc = cur_frm.doc;
  $c_obj(make_doclist(doc.doctype, doc.name),'send_for_approval','', function(){});
}

cur_frm.cscript['Send Feedback'] = function() {
  var doc = cur_frm.doc;
  $c_obj(make_doclist(doc.doctype, doc.name),'send_feedback','', function(){});
}
