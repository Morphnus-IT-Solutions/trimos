// Module CRM

cur_frm.cscript.tname = 'Lead Item Detail'
cur_frm.cscript.fname = 'lead_item_details'

$import(SMS Control)
$import(Item Common)

cur_frm.cscript.onload = function(doc, cdt, cdn) {
  if(user =='Guest'){
    hide_field(['status', 'naming_series', 'order_lost_reason', 'order_lost_details', 'customer', 'rating', 'fax', 'website', 'territory', 'TerritoryHelp', 'address_line1', 'address_line2', 'city', 'state', 'country', 'pincode', 'address', 'lead_owner', 'market_segment', 'industry', 'campaign_name', 'interested_in', 'company', 'fiscal_year', 'contact_by', 'contact_date', 'last_contact_date', 'contact_date_ref', 'to_discuss', 'More Info', 'follow_up', 'Communication History', 'cc_to', 'subject', 'message', 'Attachment Html', 'Create New File', 'lead_attachment_detail', 'Send Email', 'Email', 'Create Customer', 'Create Enquiry', 'Next Steps', 'transaction_date', 'type', 'source']);
    doc.source = 'Website';
  }
  if(!doc.status) set_multiple(dt,dn,{status:'Open'});

  if (!doc.date){ 
    doc.date = date.obj_to_str(new Date());
  }
  // set naming series
  if(user=='Guest') doc.naming_series = 'WebLead';
  
  cur_frm.add_fetch('customer', 'customer_name', 'company_name');	
}

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  // custom buttons
  //---------------
  cur_frm.clear_custom_buttons()
  if(doc.__local == 1 && !in_list(['Converted', 'Lead Lost'], doc.status)) {
    cur_frm.add_custom_button('Create Customer', cur_frm.cscript['Create Customer']);
    cur_frm.add_custom_button('Create Enquiry', cur_frm.cscript['Create Enquiry']);
    cur_frm.add_custom_button('Send SMS', cur_frm.cscript['Send SMS']);
  }

  if(doc.docstatus == 1 && in_list(['Instrument', 'Software', 'Sales', 'Accessories', 'Spares'], doc.lead_type) && !in_list(['Quotation Given', 'Order Confirmed', 'Lead Lost'], doc.status))
    cur_frm.add_custom_button('Create Quotation', cur_frm.cscript['Create Quotation']);
  else if(doc.docstatus == 1 && !in_list(['Quotation Given', 'Order Confirmed', 'Lead Lost'], doc.status))
    cur_frm.add_custom_button('Create Service Quotation', cur_frm.cscript['Create Service Quotation']);

  if (doc.status == 'Order Lost'){
    unhide_field('order_lost_reason', 'order_lost_details');
  }
  else{
    hide_field('order_lost_reason', 'order_lost_details');
  }
  if(in_list(['Quotation Given', 'Order Confirmed', 'Lead Lost'], doc.status)) set_field_permlevel('status', 1);

}


// Client Side Triggers
// ===========================================================
// ************ Status ******************
cur_frm.cscript.status = function(doc, cdt, cdn){
  cur_frm.cscript.refresh(doc, cdt, cdn);
}

/*
// *********** Country ******************
// This will show states belonging to country
cur_frm.cscript.country = function(doc, cdt, cdn) {
  var mydoc=doc;
  $c('runserverobj', args={'method':'check_state', 'docs':compress_doclist([doc])},
    function(r,rt){
      if(r.message) {
        var doc = locals[mydoc.doctype][mydoc.name];
        doc.state = '';
        get_field(doc.doctype, 'state' , doc.name).options = r.message;
        refresh_field('state');
      }
    }
  );
}
*/

cur_frm.cscript.TerritoryHelp = function(doc,dt,dn){
  var call_back = function(){
    var sb_obj = new SalesBrowser();        
    sb_obj.set_val('Territory');
  }

  loadpage('Sales Browser',call_back);
}

// Create New File
// ===============================================================
cur_frm.cscript['Create New File'] = function(doc){
  new_doc("File");
}

// fetch item details
// -------------------
cur_frm.add_fetch('item_code', 'product_code', 'product_code');
cur_frm.add_fetch('item_code', 'item_name', 'item_name');
cur_frm.add_fetch('item_code', 'item_group', 'item_group');
cur_frm.add_fetch('item_code', 'stock_uom', 'uom');
cur_frm.add_fetch('item_code', 'item_type', 'item_type');
cur_frm.add_fetch('item_code', 'brand', 'brand');
cur_frm.add_fetch('item_code', 'description', 'description');

/*
cur_frm.cscript.item_code = function(doc, dt, dn){
	var d = locals[dt][dn];
	if(d.item_code){
		get_server_fields('get_item_details', d.item_code, 'lead_item_details', doc, dt, dn, 1);
	}
}
*/

// fetch customer details
// ------------------------
cur_frm.add_fetch('customer', 'customer_group', 'customer_group');
cur_frm.add_fetch('customer', 'customer_name', 'company_name');
cur_frm.add_fetch('customer', 'territory', 'territory');
cur_frm.add_fetch('customer', 'zone', 'zone');
cur_frm.add_fetch('customer', 'website', 'website');

cur_frm.cscript.customer = function(doc, dt, dn) {
  if(doc.customer){
      var callback = function(r, rt){
         var doc = locals[cur_frm.doctype][cur_frm.docname];
         cur_frm.refresh();
      }
      $c_obj(make_doclist(doc.doctype, doc.name), 'get_customer_details', '',callback);
  }
}


// fetch serial no details
// -------------------------
cur_frm.add_fetch('serial_no', 'item_code', 'item_code');	
cur_frm.add_fetch('serial_no', 'brand', 'brand');
cur_frm.add_fetch('serial_no', 'description', 'description');
cur_frm.add_fetch('serial_no', 'product_code', 'product_code');

get_contact_person_query = function(doc){
  return 'SELECT CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.fields_dict['end_user'].get_query = cur_frm.fields_dict['purchase_manager'].get_query = cur_frm.fields_dict['qa_manager'].get_query = function(doc, cdt, cdn) {
  if(!doc.customer){
    alert("Please Enter Customer Name");
    validated = false;
  }
  return get_contact_person_query(doc);
}

// Create New Customer
// ===============================================================
cur_frm.cscript['Create Customer'] = function(){
  var doc = cur_frm.doc;
  $c('runserverobj',args={ 'method':'check_status', 'docs':compress_doclist([doc])},
    function(r,rt){
      if(r.message == 'Converted'){
        msgprint("This lead is already converted to customer");
      }
      else{
        n = createLocal("Customer");
        $c('dt_map', args={
          'docs':compress_doclist([locals["Customer"][n]]),
          'from_doctype':'Lead',
          'to_doctype':'Customer',
          'from_docname':doc.name,
          'from_to_list':"[['Lead', 'Customer']]"
        }, 
        function(r,rt) {
          loaddoc("Customer", n);
        }
        );
      }
    }
  );
}

// send email
// ===============================================================
cur_frm.cscript['Send Email'] = function(doc,cdt,cdn){
  if(doc.__islocal != 1){
    $c_obj(make_doclist(doc.doctype, doc.name),'send_mail','',function(r,rt){});
  }else{
    msgprint("Please save lead first before sending email")
  }
}

// Create New Enquiry
// ===============================================================
cur_frm.cscript['Create Enquiry'] = function(){
  var doc = cur_frm.doc;
  $c('runserverobj',args={ 'method':'check_status', 'docs':compress_doclist([doc])},
    function(r,rt){
      if(r.message == 'Converted'){
        msgprint("This lead is now converted to customer. Please create enquiry on behalf of customer");
      }
      else{
        n = createLocal("Enquiry");
        $c('dt_map', args={
          'docs':compress_doclist([locals["Enquiry"][n]]),
          'from_doctype':'Lead',
          'to_doctype':'Enquiry',
          'from_docname':doc.name,
          'from_to_list':"[['Lead', 'Enquiry']]"
        }
        , function(r,rt) {
            loaddoc("Enquiry", n);
          }
        );
      }
    }
  );
}

//get query select Territory
cur_frm.fields_dict['territory'].get_query = function(doc,cdt,cdn) {
  return 'SELECT `tabTerritory`.`name`,`tabTerritory`.`parent_territory` FROM `tabTerritory` WHERE `tabTerritory`.`is_group` = "No" AND `tabTerritory`.`docstatus`!= 2 AND `tabTerritory`.%(key)s LIKE "%s" ORDER BY  `tabTerritory`.`name` ASC LIMIT 50';
}

cur_frm.cscript['Create Quotation'] = function() {
  var doc = cur_frm.doc;
  n = createLocal('Quotation');
  $c('dt_map', args={
    'docs':compress_doclist([locals["Quotation"][n]]),
    'from_doctype':'Lead',
    'to_doctype':'Quotation',
    'from_docname':doc.name,
    'from_to_list':"[['Lead','Quotation'],['Lead Item Detail','Quotation Detail']]"
    }, function(r,rt) {
       loaddoc('Quotation', n);
    }
  );
}

cur_frm.cscript['Create Service Quotation'] = function() {
  var doc = cur_frm.doc;
  n = createLocal('Service Quotation');
  $c('dt_map', args={
    'docs':compress_doclist([locals['Service Quotation'][n]]),
    'from_doctype':doc.doctype,
    'to_doctype':'Service Quotation',
    'from_docname':doc.name,
    'from_to_list':"[['Lead','Service Quotation'],['Service Item Detail','Service Quotation Detail']]"
    }, function(r,rt) {
       loaddoc('Service Quotation', n);
    }
  );
}

cur_frm.fields_dict['follow_up'].grid.get_field("contact_person").get_query = function(doc, cdt, cdn) {
  return 'SELECT `tabContact`.contact_name FROM `tabContact` WHERE `tabContact`.is_customer = 1 AND `tabContact`.customer_name = "'+ doc.customer_name+'" AND `tabContact`.contact_name LIKE "%s" ORDER BY `tabContact`.contact_name ASC LIMIT 50';
}

cur_frm.cscript.contact_person = function(doc, cdt, cdn){
  var d = locals[cdt][cdn];
  var callback = function(){refresh_field('contact_details');}
  get_server_fields('get_contact_person_details',d.contact_person, 'follow_up', doc, cdt, cdn, 1, callback);
}

cur_frm.cscript.order_lost = function(doc, cdt, cdn){
  if(doc.order_lost == "Yes")
    unhide_field(['reason_for_lost_order']);
  else
    hide_field(['reason_for_lost_order']);
}

