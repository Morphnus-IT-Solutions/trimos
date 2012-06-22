// --------
// refresh
// --------
cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  cur_frm.clear_custom_buttons();
  if(doc.docstatus == 1 && doc.status != 'Closed'){
    cur_frm.add_custom_button('Create Service Report', cur_frm.cscript['Create Service Report']);
    cur_frm.add_custom_button('Make Visit Report', cur_frm.cscript['Create Visit Report']);
  }
    
  if(!doc.__islocal) unhide_field('Send for Approval');
  else hide_field('Send for Approval');
  
  if(inList(user_roles, 'CRM Manager') && !doc.__islocal) unhide_field('Send Feedback');
  else hide_field('Send Feedback');
  
}


// sales person details
cur_frm.add_fetch('prepared_by', 'territory', 'territory');


// customer details
cur_frm.add_fetch('customer', 'territory', 'territory');


// item details
cur_frm.add_fetch('item_code', 'brand', 'brand');
cur_frm.add_fetch('item_code', 'product_code', 'product_code');


cur_frm.fields_dict['unscheduled_visit_details'].grid.get_field("against_document_no").get_query = function(doc, cdt, cdn){
 var d = locals[this.doctype][this.docname];
 return 'SELECT `tab'+d.against_document+'`.`name` FROM `tab'+d.against_document+'` WHERE `tab'+d.against_document+'`.`name` LIKE "%s" ORDER BY `tab'+d.against_document+'`.`name` DESC LIMIT 50'
}

cur_frm.cscript['Create Visit Report'] = function(){
  var doc = cur_frm.doc;
  var flag = cur_frm.cscript.check_no_of_visits(doc, 1);  // to check the no of visits selected to create report
  if (doc.docstatus == 1) { 
  n = createLocal("Visit Report");
  $c('dt_map', args={
	  'docs':compress_doclist([locals["Visit Report"][n]]),
	  'from_doctype':'Monthly Visit Schedule',
	  'to_doctype':'Visit Report',
	  'from_docname':doc.name,
    'from_to_list':"[['Scheduled Visit Details', 'Visit Report Detail'], ['Unscheduled Visit Details', 'Visit Report Detail']]"
  }
  , function(r,rt) {
    loaddoc("Visit Report", n);
    }
    );
  }
}

cur_frm.cscript['Create Service Report'] = function(){
  var doc = cur_frm.doc;
  var cdt = cur_frm.cdt;
  var cdn = cur_frm.cdn;
  var flag = cur_frm.cscript.check_no_of_visits(doc, 2);  // to check the no of visits selected to create report
  var sv = getchildren('Scheduled Visit Details', doc.name, 'scheduled_visit_details');
  for(var i = 0;i<sv.length;i++){
    if(sv[i].select == 1 && flag == 1 && sv[i].against_document == 'Serial No')
      cur_frm.cscript.create_service_report(doc, sv[i]);
  }
  var uv = getchildren('Unscheduled Visit Details', doc.name, 'unscheduled_visit_details');
  for(var i = 0;i<uv.length;i++){
    if(uv[i].select == 1 && flag == 1 && uv[i].against_document == 'Serial No')
      cur_frm.cscript.create_service_report(doc, uv[i]);
  }
}

cur_frm.cscript.check_no_of_visits = function(doc, val){
  var flag = 0;
  var schedule = getchildren('Scheduled Visit Details', doc.name, 'scheduled_visit_details');
  for(var i = 0; i < schedule.length; i++){
    if(flag == 0 && schedule[i].select == 1 && schedule[i].visit_report_id)
      flag = 3;    
    else if(flag == 0 && schedule[i].select == 1)
      flag = 1;
    else if(flag == 1 && schedule[i].select == 1 && val == 2)
      flag = 2;
  }
  var unschedule = getchildren('Unscheduled Visit Details', doc.name, 'unscheduled_visit_details');
  for(var i = 0; i < unschedule.length; i++){
    if(flag == 0 && unschedule[i].select == 1 && unschedule[i].visit_report_id)
      flag = 3;
    else if(flag == 0  && unschedule[i].select == 1)
      flag = 1;
    else if(flag == 1 && unschedule[i].select == 1 && val == 2)
      flag = 2;
  }
  
  if(flag == 0){
    alert("Please select atleast one visit for which you want to create report");
  }
  else if(flag == 2){
    alert("You can create service report for only one schedule at a time. Please select only one scheduled visit");
  }
  else if(flag == 3){
    alert("You have already created report.");
  }
  return flag;
}

cur_frm.cscript.create_service_report = function(doc, det){
  var callback = function(r, rt){
    var r = r.message;
    var sr = LocalDB.create('Service Report');
    sr = locals['Service Report'][sr];
    sr.scheduled_date = det.scheduled_date;
    sr.customer = det.customer;
    sr.customer_address = r.customer_address;
    sr.address_display = r.address_display;
    sr.purpose = det.purpose;
    sr.amc_visit_no = r.amc_visit_no;
    sr.serial_no = det.against_document_no;
    sr.brand = r.brand;
    sr.product_code = det.product_code;
    sr.version = r.version;
    loaddoc("Service Report",sr.name);
  }
  args = "{'customer_name':'" + det.customer + "','serial_no':'" + det.against_document_no + "','purpose':'" + det.purpose + "'}";
  $c_obj(make_doclist(doc.doctype, doc.name), 'get_other_details', args, callback);
}
