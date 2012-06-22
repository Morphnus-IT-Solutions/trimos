pscript['onload_MIS'] = function() {

  // Hide all except for Module options
  hide_options();

  // It will print the following messages before loading (cool look nothing else......)
  add_sel_options($i('module'), ['Loading Module...']);
  add_sel_options($i('transaction'), ['Loading Transactions...']);
  add_sel_options($i('company'), ['Loading Companies...']);
   
  // Get Values of Module, Company, Fiscal Year, Month and Fiscal Year Start Dates
  get_values();
  
  // Setup MIS
  mis_setup();

  // GO Button
  var btn2 = $a('go', 'button');
  btn2.innerHTML = 'GO';
  btn2.onclick = function() {get_result();}

  //Reset Button
  var btn1 = $a('reset', 'button');
  btn1.innerHTML = 'Reset';
  btn1.onclick = function() {reset_mis();}
}

// Hide Options
// -----------------
var hide_options = function() {
  op_list = ['trans','grp_by','sum','comp','type','fyear','per','from_fyear','to_fyear','from_date','to_date','go','filter'];
  for(var i = 0; i < op_list.length ; i++) $dh(op_list[i]);
}


// Load Modules, Companies, Fiscal Year, Year Start Dates 
// ---------------------------------------------------------
var get_values = function() {

  // this customization is done because of Service Module which will have (Service Quotation, Service Order)
  empty_select($i('module'));
  add_sel_options($i('module'),['Select Module...','Sales','Service']);
  $c_obj('MIS Control','get_comp','', function(r,rt) {    
    // Module
    //empty_select($i('module'));
    //add_sel_options($i('module'), add_lists(['Select Module...'], r.message.type), 'Select Module...');
    
    // Company
    pscript.companies = r.message.company;
    
    // Fiscal Year
    pscript.fiscal_years = r.message.fiscal_year;
    
    // Months
    pscript.months = r.message.month;
    
    // Fiscal Year Start Dates
    pscript.year_start_dates = r.message.start_dates;
  });
}

// MIS Setup (contains all On Change function i.e. which field will be visible on changing particular field)
// -----------------------------------------------------------------------------------------------------------
var mis_setup = function() {
  // Enable Transaction and Disable Module
  $i('module').onchange = function(){
    get_transactions();  // Gets Transactions and Group By options based on Module selected
    $ds('trans');
    $i('module').disabled = true;
  }

  // Enable Group By and Disable Transaction
  $i('transaction').onchange = function(){
    empty_select($i('group_by'));
    add_sel_options($i('group_by'), add_lists(['Group By...'], pscript.group_by), 'Group By...');
    $ds('grp_by');
    $i('transaction').disabled = true;
  }

  // Enable Sum Of and Disable Group By
  $i('group_by').onchange = function(){
    empty_select($i('sum_of'));
    if(sel_val($i('module')) == 'Sales') add_sel_options($i('sum_of'),['Select Sum Of...','Amount','Quantity']);
    else if(sel_val($i('module')) == 'Service') add_sel_options($i('sum_of'),['Select Sum Of...','Amount','No. of Visit']);
    $ds('sum');
    $i('group_by').disabled = true;
  }

  // Enable Company and Disable Sum Of
  $i('sum_of').onchange = function(){
    empty_select($i('company'));
    add_sel_options($i('company'), add_lists(['Select Company...'], pscript.companies), 'Select Company...');
    $ds('comp');
    $i('sum_of').disabled = true;
  }   

  // Enable MIS Type and Disable Company
  $i('company').onchange = function(){
    empty_select($i('mis_type'));
    add_sel_options($i('mis_type'),['Select MIS Type...','Single Year','Multiple Years']);
    $ds('type');
    $i('company').disabled = true;
  }

  // Enable options based on MIS Type selected and Disable MIS Type
  $i('mis_type').onchange = function(){
    type = sel_val($i('mis_type'));
    if(type == 'Single Year'){
      // get fiscal years
      empty_select($i('fiscal_year'));
      add_sel_options($i('fiscal_year'), add_lists(['Select Fiscal Year...'], pscript.fiscal_years), 'Select Fiscal Year...');
      $ds('fyear');
    }
    else if(type == 'Multiple Years'){
      // get fiscal years
      empty_select($i('from_fiscal_year'));
      add_sel_options($i('from_fiscal_year'), add_lists(['Select Fiscal Year...'], pscript.fiscal_years), 'Select Fiscal Year...');
      $ds('from_fyear');
    }
    $i('mis_type').disabled = true;
  }
  
  // Enable period and disable Fiscal year
  $i('fiscal_year').onchange = function(){
    empty_select($i('period'));
    add_sel_options($i('period'),['Select Period...','Annually','Half Yearly','Quarterly','Monthly']);
    $ds('per');
    $i('fiscal_year').disabled = true;
  }
  
  // Enable GO button and disable Period
  $i('period').onchange = function(){
    $ds('go');
    $i('period').disabled = true;
  }
  
  // Enable To Fiscal Year and disable From Fiscal Year
  $i('from_fiscal_year').onchange = function(){
    // get fiscal years
    empty_select($i('to_fiscal_year'));
    add_sel_options($i('to_fiscal_year'), add_lists(['Select Fiscal Year...'], pscript.fiscal_years), 'Select Fiscal Year...');
    $ds('to_fyear');
    $i('from_fiscal_year').disabled = true;
  }
  
  // Enable From Date, To Date, Go button and disable To Fiscal Year
  $i('to_fiscal_year').onchange = function(){
    // get from Months
    empty_select($i('from_month'));
    add_sel_options($i('from_month'), add_lists([''], pscript.months), '');
    // get to Months
    empty_select($i('to_month'));
    add_sel_options($i('to_month'), add_lists([''], pscript.months), '');
    $i('to_fiscal_year').disabled = true;
    $ds('from_date');
    $ds('to_date');
    $ds('go');
  }
  
  // get dates based on month (i.e. Jan - 31, Feb - 28, Apr - 30 etc.)
  $i('from_month').onchange = function() { get_days(sel_val($i('from_month')),'from');}
  $i('to_month').onchange = function() { get_days(sel_val($i('to_month')),'to');}
}

// Loading Transactions and Group By options based on module
// -----------------------------------------------------------
var get_transactions = function() {
  $c_obj('MIS Control','get_trans_group',sel_val($i('module')), function(r,rt) {    
    // transactions
    empty_select($i('transaction'));
    add_sel_options($i('transaction'), add_lists(['Select Transaction...'], r.message.stmt_type), 'Select Transaction...');
    
    // group by
    pscript.group_by = r.message.group_by;
  });
}


// Get Days based on Month Selected
// ---------------------------------------
var get_days = function(month,field) {
  $c_obj('MIS Control','get_days',month,function(r,rt){
    empty_select($i(field+'_day'));
    add_sel_options($i(field+'_day'), add_lists([], r.message.days), '');
  });
}


// Get Results
// -----------------------
var get_result = function(){
  $i('period').disabled = true;
  $i('from_month').disabled = true;
  $i('to_month').disabled = true;
  $i('from_day').disabled = true;
  $i('to_day').disabled = true;

  var flag = 1;
  // check whether from date and to date are of particular fiscal year
  if(sel_val($i('mis_type')) == 'Multiple Years' && sel_val($i('from_month')) != '' && sel_val($i('to_month')) != ''){
    var is_valid = validate_dates(sel_val($i('from_fiscal_year'))).split('~~~');
    if(is_valid[0] == 'Valid') flag = 1;
    else flag = 0;
  }

  var trans = sel_val($i("transaction"));
  if(trans == 'Purchase Order') var trans_det = 'PO';
  else var trans_det = trans;

  $ds('filter');

  if(flag == 1)  set_stmt(trans, trans_det);
}


// check whether dates entered are within particular fiscal_year
// -------------------------------------------------------------------
var validate_dates = function(fiscal_year){
  var month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var from_mon = sel_val($i('from_month'));
  var to_mon = sel_val($i('to_month'));
  var from_day = sel_val($i('from_day'));
  var to_day = sel_val($i('to_day'));
  var start_date = pscript.year_start_dates[fiscal_year];
  var st_mon = cint(month.indexOf(from_mon)) + 1;
  var ed_mon = cint(month.indexOf(to_mon)) + 1;
  var fiscal_start_month = start_date.split('-')[1];
  var next_fiscal_year = cint(start_date.split('-')[0]) + 1;
  var current_year = ''
  var next_year = ''
  
  // CASE - 1 : Jan - Mar (Valid)
  // ===============================
  if(st_mon < fiscal_start_month && ed_mon < fiscal_start_month){
    current_year = cint(start_date.split('-')[0]) + 1;
    next_year  = cint(start_date.split('-')[0]) + 1;
  }
  // Case - 2 : Apr - Dec (Valid)
  // ===============================
  else if(st_mon >= fiscal_start_month && ed_mon <= 12 && ed_mon >= fiscal_start_month ){
    current_year = start_date.split('-')[0];
    next_year  = start_date.split('-')[0];
  }
  // Case 3 : Jan - May (Invalid)
  // ===============================
  else if(st_mon < fiscal_start_month && ed_mon >= fiscal_start_month){
    current_year = cint(start_date.split('-')[0]) + 1;
    next_year  = cint(start_date.split('-')[0]) + 2;
  }
  // Case 4 : Dec - Apr ( ??? )
  // this entry is actully invalid but it will show data from Apr to dec for that particular year
  
  // all dates in mm/dd/yyyy hh:mm:ss format
  var begin_date = start_date.split('-')[1]+"/"+start_date.split('-')[2]+"/"+start_date.split('-')[0]+" 12:00:00 AM"
  var end_date = start_date.split('-')[1]+"/"+start_date.split('-')[2]+"/"+next_fiscal_year+" 12:00:00 AM"
  var check_date_from =  st_mon+"/"+from_day+"/"+current_year+" 12:00:00 AM"
  var check_date_to =  ed_mon+"/"+to_day+"/"+next_year+" 12:00:00 AM"
  
  var period_from_date = '';
  var period_to_date = '';
  var b,e,cf,ct;
	b = Date.parse(begin_date);
	e = Date.parse(end_date);
	cf = Date.parse(check_date_from);
	ct = Date.parse(check_date_to);
  if((cf <= e && cf >= b) && (ct <= e && cf >= b)){
    period_from_date = current_year+"-"+st_mon+"-"+from_day
    period_to_date = next_year+"-"+ed_mon+"-"+to_day
    return 'Valid~~~'+cstr(period_from_date)+'~~~'+cstr(period_to_date)
  }
  else{
    msgprint("Please enter appropriate From Date and To Date");
    return 'Invalid~~~'   
  }
}

var set_stmt = function(trans, trans_det) {
  if(!pscript.mis_lst) pscript.mis_lst = new Listing('');
  
  var module = sel_val($i("module"));            // get module
  var group_by = sel_val($i("group_by"));        // get group by field on this you will group by your result
  var company = sel_val($i("company"));          // get company
  var sum_of = sel_val($i("sum_of"));            // get requirement
  var mis_type = sel_val($i("mis_type"));        // get MIS Type
  pscript.curr_format = ''
  // check whether MIS is reqd on Amount or Qty
  if(sum_of == 'Amount'){
    var sum_val = 'amount';
    pscript.curr_format = '/100000'
  }
  else if(sum_of == 'Quantity') var sum_val = 'qty';
  else if(sum_of == 'No. of Visit') var sum_val = 'no_of_visit';
  
  // Get Query Value and Column Names based on MIS Type
  if(mis_type == 'Single Year') var query_columns = get_single_year_query_value(trans, trans_det, sum_val);
  else var query_columns = get_multiple_years_query_value(trans, trans_det, sum_val);
  
  // Get column names and values based on Group By value selected
  var group = get_group_by(module, trans, trans_det, group_by);
  
  var lst = pscript.mis_lst
  
  // Gets columns to be appended in Listing Objects
  get_lst_details(lst,group,group_by,query_columns.split('~~~')[1],mis_type);
  
  // get value of additional info field (Eg. description for Item etc...)
  if((group.split(',')).length > 1) add_info = (group.split(','))[1]+",";
  else add_info = "";
    
  // get value of all columns for query
  if(mis_type == 'Single Year') var query_value = query_columns.split('~~~')[0]+'SUM(`tab'+trans_det+' Detail`.'+sum_val+')'+pscript.curr_format+' as Total';
  else var query_value = query_columns.split('~~~')[0];
    
  // check for company
  if(company == 'All') var com = '';
  else var com = '`tab'+trans+'`.company = "'+company+'" AND';
  
  // get condition for query
  if(mis_type == 'Single Year'){
   var fiscal_year = sel_val($i("fiscal_year"));
   var condition = '`tab'+trans+'`.fiscal_year = "'+fiscal_year+'"  AND `tab'+trans_det+' Detail`.parent = `tab'+trans+'`.name  AND `tab'+trans+'`.transaction_date >= CAST("'+pscript.year_start_dates[fiscal_year]+'" AS DATE) AND `tab'+trans_det+' Detail`.docstatus=1'
  }
  else{
    var from_month = sel_val($i("from_month"));
    var to_month = sel_val($i("to_month"));
    if(from_month != "" && to_month != "") var condition = '`tab'+trans_det+' Detail`.parent = `tab'+trans+'`.name  AND ('+query_columns.split('~~~')[2]+') AND `tab'+trans_det+' Detail`.docstatus=1'
    else var condition = '`tab'+trans_det+' Detail`.parent = `tab'+trans+'`.name  AND `tab'+trans_det+' Detail`.docstatus=1'
  }
  
  // get query
  build_query(module, (group.split(','))[0], group_by, add_info, query_value, com, condition, trans, trans_det, lst);
}


// Get Column Names and its value for Query of MIS Type Single Year
// --------------------------------------------------------------------
var get_single_year_query_value = function(trans, trans_det, sum_val){
  var col_names = [];
  var query_val = '';
  var month_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var fiscal_year = sel_val($i("fiscal_year"));
  var period = sel_val($i("period"));
  var start_month = cint(pscript.year_start_dates[fiscal_year].split('-')[1]);
  
  // Annually
  // --------------
  if(period == 'Annually'){
    col_names.push(fiscal_year);
    query_val = 'SUM(`tab'+trans_det+' Detail`.'+sum_val+')'+pscript.curr_format+' AS "'+fiscal_year+'",'
  }
  
  // Half Yearly
  // ----------------
  else if(period == 'Half Yearly'){
    // first half (works in both cases (1)FY starts in APRIL or (2)FY starts in JAN)
    var first_half = month_name[start_month-1]+' to '+month_name[start_month+4];
	var second_half = '';
	col_names.push(first_half);
    query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) BETWEEN '+(start_month)+' AND '+(start_month+5)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+first_half+'",';
    
    // second half (little bit tedious coz. need to consider two cases i.e (1)FY starts in APRIL or (2)FY starts in JAN)
    if(start_month == 1){  // this is case when fiscal year starts with JAN
      second_half = month_name[start_month+5]+' to '+month_name[start_month+11];
	  col_names.push(second_half);
    }
	else{  //this is case when fiscal year starts with other than JAN
      second_half = month_name[start_month+5]+' to '+month_name[start_month-2];
	  col_names.push(second_half);
	}
    query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) NOT BETWEEN '+(start_month)+' AND '+(start_month+5)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+second_half+'",';
  }
  
  // Quarterly
  // ---------------
  else if(period == 'Quarterly'){
    var length_1 = (month_name.length - start_month + 1) / 3; //this gives the total no. of times we need to iterate for quarter
    var val = length_1 % 4;
    var q_no = 1;
	var quarter1 = '';
	var quarter2 = '';
    for(i=0;i<length_1;i++){
      var value = 3*i + val;
      quarter1 = 'Q'+q_no+' ('+month_name[value]+' to '+month_name[value+2]+')';
	  col_names.push(quarter1);
      query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) BETWEEN '+(value+1)+' AND '+(value+3)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+quarter1+'",';
      q_no += 1;
    }
    var length_2 = (start_month - 1) / 3; //this gives the total no. of times we need to iterate for quarter (this is required only if fiscal year starts from april)
    for(i = 0;i<length_2;i++){
      quarter2 = 'Q'+q_no+' ('+month_name[3*i]+' to '+month_name[3*i+2]+')';
	  col_names.push(quarter2);
      query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) BETWEEN '+(3*i+1)+' AND '+(3*i+3)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+quarter2+'",';
      q_no += 1;
    }
  }
  
  // Monthly
  // -------------
  else if(period == 'Monthly'){
    for(i = start_month-1;i<month_name.length;i++){
      col_names.push(month_name[i]);
      query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) = '+(i+1)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+month_name[i]+'",'
    }  
    for(i = 0;i<start_month-1;i++){
      col_names.push(month_name[i]);
      query_val += 'SUM(CASE WHEN MONTH(`tab'+trans+'`.transaction_date) = '+(i+1)+' THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+month_name[i]+'",'
    }
  }
  
  ret = cstr(query_val)+'~~~'+cstr(col_names)
  return ret
}


// Get Column Names and its value for Query of MIS Type Multiple Years
// --------------------------------------------------------------------
var get_multiple_years_query_value = function(trans, trans_det, sum_val){
  var col_names = [];
  var query_val = '';
  var date_cond = '';
  var from_fiscal_year = sel_val($i("from_fiscal_year"));
  var to_fiscal_year = sel_val($i("to_fiscal_year"));
  var from_month = sel_val($i("from_month"));
  var to_month = sel_val($i("to_month"));
  
  // get no. of fiscal years between from and to fiscal year
  var start_year = from_fiscal_year.split('-')[1] // eg. from fiscal year 2008-2009 . this gives value 2009
  var end_year = to_fiscal_year.split('-')[0] // eg. to fiscal year 2010-2011 . this gives value 2010
  var d = cint(end_year - start_year)
  
  /* There are two Cases 
      1. From Fiscal Year -> 2008-2009
         To Fiscal Year -> 2010-2011
      2. From Fiscal Year -> 2010-2011   
         To Fiscal Year -> 2008-2009         
  */
  
  if(d < 0) var diff = Math.abs(d) - 2; // For Case 2. we need to traverse for two less than diff
  else var diff = Math.abs(d)  // For Case 1.
  
  col_names.push(from_fiscal_year);
  /*if
      there is from to month specified
    else
      year on year analysis
  */
  if(from_month != "" && to_month != ""){
    query_val += 'SUM(CASE WHEN (`tab'+trans+'`.fiscal_year = "'+from_fiscal_year+'" and (`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(from_fiscal_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(from_fiscal_year).split('~~~')[2]+'" AS DATE))) THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+from_fiscal_year+'",'
    date_cond += '(`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(from_fiscal_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(from_fiscal_year).split('~~~')[2]+'" AS DATE)) OR '
  }
  else
    query_val += 'SUM(CASE WHEN `tab'+trans+'`.fiscal_year = "'+from_fiscal_year+'" THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+from_fiscal_year+'",'
  
  if(diff > 0){
    if(d < 0) var year = cint(start_year) - 2; // Case 2.
    else var year = cint(start_year);
    var next_year = 0
    var f_year = ''
    for(var i = 0; i < diff ; i++){
      next_year = year+1;
      f_year = year+'-'+next_year;
      col_names.push(f_year);
      if(from_month != "" && to_month != ""){
        query_val += 'SUM(CASE WHEN (`tab'+trans+'`.fiscal_year = "'+f_year+'" and (`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(f_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(f_year).split('~~~')[2]+'" AS DATE))) THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+f_year+'",'
        date_cond += '(`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(f_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(f_year).split('~~~')[2]+'" AS DATE)) OR '
      }
      else
        query_val += 'SUM(CASE WHEN `tab'+trans+'`.fiscal_year = "'+f_year+'" THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+f_year+'",'
      if(d > 0) year += 1; // Case 2.
      else if(d < 0) year -= 1;
    }
  }
  col_names.push(to_fiscal_year);
  if(from_month != "" && to_month != ""){
    query_val += 'SUM(CASE WHEN (`tab'+trans+'`.fiscal_year = "'+to_fiscal_year+'" and (`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(to_fiscal_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(to_fiscal_year).split('~~~')[2]+'" AS DATE))) THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+to_fiscal_year+'"'
    date_cond += '(`tab'+trans+'`.transaction_date BETWEEN CAST("'+validate_dates(to_fiscal_year).split('~~~')[1]+'" AS DATE) AND CAST("'+validate_dates(to_fiscal_year).split('~~~')[2]+'" AS DATE))'
  }
  else
    query_val += 'SUM(CASE WHEN `tab'+trans+'`.fiscal_year = "'+to_fiscal_year+'" THEN `tab'+trans_det+' Detail`.'+sum_val+' ELSE NULL END)'+pscript.curr_format+' AS "'+to_fiscal_year+'"'
  
  ret = cstr(query_val)+'~~~'+(col_names)+'~~~'+cstr(date_cond)
  return ret
}


// Get column names and values for query based on Group By value selected
// -------------------------------------------------------------------------- 
var get_group_by = function(module, trans, trans_det, group_by){
  if(group_by == 'Item')
    return '`tab'+trans_det+' Detail`.item_code,`tab'+trans_det+' Detail`.description AS Description,Description'
  else if(group_by == 'Brand')
    return '`tab'+trans_det+' Detail`.brand'
  else if(group_by == 'Item Type')
    return '`tabItem`.item_type'
  else if(group_by == 'Customer')
    return '`tab'+trans+'`.customer,`tab'+trans+'`.territory AS Territory,Territory'
  else if(group_by == 'Customer Group')
    return '`tab'+trans+'`.customer_group'
  else if(group_by == 'Territory')
    return '`tab'+trans+'`.territory'
  else if(group_by == 'Zone')
    return '`tab'+trans+'`.zone'
  else if(group_by == 'Item Group')
    return '`tabItem`.item_group'
  else if(group_by == 'Sales Person')
    return '`tabSales Team`.sales_person'
  else if(group_by == 'Serial No')
    return '`tab'+trans_det+' Detail`.serial_no,`tab'+trans_det+' Detail`.description AS Description,Description'
}


var get_lst_details = function(lst,group,group_by,columns,mis_type){
  lst.colwidths = ['5%','10%'];
  lst.colnames = ['Sr',group_by];
  lst.coltypes = ['Data','Link'];
  lst.coloptions = ['',group_by];
  
  var grp = group.split(',');
  var group_len = grp.length;  // if length is greater than 1 then there might be some additional info abt particular grp 
  var col = columns.split(',');
  var col_length = col.length; // this gives the no. of columns required
  var width = ''
  
  // This step is reqd coz if there is monthly MIS we also need to add total in end
  if(mis_type == 'Single Year') var tot = 72;
  else var tot = 85;
  
  // set width for columns based on no. of columns
  if(group_len > 1) width = tot/(col_length+1); //(col_length+1) coz there will also be add detail field
  else width = tot/col_length;
  
  if(group_len > 1){
    lst.colwidths.push(width+"%");
    lst.colnames.push(grp[2]);
    lst.coltypes.push("Data");
    lst.coloptions.push("");
  }
  
  for(var i = 0; i< col.length ; i++){
    lst.colwidths.push(width+"%");
    lst.colnames.push(col[i]);
    lst.coltypes.push("Currency");
    lst.coloptions.push("");
  }
  
  if(mis_type == 'Single Year'){
    lst.colwidths.push("13%");
    lst.colnames.push("Total");
    lst.coltypes.push("Currency");
    lst.coloptions.push("");
  }
}


var build_query = function(module, group, group_by, add_info, query_val, com, condition, trans, trans_det, lst){
  var add_tables = '`tab'+trans+'`,`tab'+trans_det+' Detail`,`tabItem`,`tabSales Team`'
  var add_cond = ' AND `tabItem`.name = `tab'+trans_det+' Detail`.item_code AND `tabSales Team`.parent = `tab'+trans+'`.name'

  lst.get_query = function() {
    this.group_by =  'GROUP BY '+group;
    this.query = repl('SELECT %(st)s AS "'+group_by+'", %(info)s %(q)s FROM `tab'+trans+'`,`tab'+trans_det+' Detail` WHERE  %(com)s %(cond)s',{st:group,info:add_info,q:query_val,com:com,cond:condition});
    this.query_max = repl('SELECT count(DISTINCT '+group+') from `tab'+trans+'`,`tab'+trans_det+' Detail` WHERE %(com)s %(cond)s',{st:group,info:add_info,q:query_val,com:com,cond:condition});
  }
  lst.is_std_query = 1;
  lst.set_default_sort(group, 'ASC');
   
  // Add sorting on all the columns
  for(var i = 1; i < lst.colwidths.length; i++) lst.add_sort(i,'`'+lst.colnames[i]+'`');
    
  // filter  
  if(!lst.filter_area) lst.make($i('filter'));
  lst.remove_all_filters();
  
  lst.add_filter('Item','Link','Item',trans_det+' Detail','item_code');
  lst.add_filter('Item Group','Link','Item Group','Item','item_group');
  lst.add_filter('Item Type','Link','Item Type','Item','item_type');
  lst.add_filter('Brand','Link','Brand',trans_det+' Detail','brand');
  lst.add_filter('Customer','Link','Customer',trans,'customer');
  lst.add_filter('Customer Group','Link','Customer Group',trans,'customer_group');
  lst.add_filter('Territory','Link','Territory',trans,'territory');
  lst.add_filter('Zone','Link','Zone',trans,'zone');
  lst.add_filter('Sub Category','Select',['All','DI','INR'].join(NEWLINE),trans,'sub_category');
  lst.add_filter('Sales Person','Link','Sales Person','Sales Team','sales_person');
  
  if(module == 'Service') lst.add_filter('Serial No','Link','Serial No',trans_det+' Detail','serial_no');

  lst.run();

  // Listing Callback
  // -----------------
  lst.onrun = function() {
    // add filters
    fil_cond = filter_conditions(this.filters);
    args = {'query_val':query_val,'tables':add_tables,'company':com,'cond':condition,'add_cond':add_cond,'fil_cond':fil_cond};
    var callback = function(r,rt){
      totals = r.message;
      var col_names = [];
      for(var i = 0; i < lst.coltypes.length; i++){
        if(lst.coltypes[i] == 'Currency' || lst.coltypes[i] == 'Int' || lst.coltypes[i] == 'Float'){
          col_names.push(lst.colnames[i]);
        }
      }
      $i('mis_totals').innerHTML = '<br><br><h3>Totals :</h3>'
      var mis_tot = make_table($i('mis_totals'),2,col_names.length+1,'70%',[],{border:'1px solid #AAA',padding:'2px'});  
      $td(mis_tot, 0, 0).innerHTML = 'Period';
      $td(mis_tot, 1, 0).innerHTML = 'Totals';
      
      for(var i = 0; i < col_names.length; i++){
        $td(mis_tot, 0, i+1).innerHTML = col_names[i];
        $td(mis_tot, 1, i+1).innerHTML = cstr(flt(totals[col_names[i]]));
      }
    }
    $c_obj('MIS Control','get_totals',docstring(args),callback);
  }
  lst.reset_tab();
}


// Additional Conditions if Filter is Selected
// --------------------------------------------
var filter_conditions = function(filters){
  var cond = '';
  for(var i in filters) {
    var f = filters[i];
    var val = f.get_value();
    var c = f.condition;
    if(!c)c='=';
    if(val && c.toLowerCase()=='like')val += '%';
    if(f.tn && val && !in_list(['All','Select...',''],val)) 
      cond += ' AND `tab'+f.tn+'`.'+f.fn+' '+c+' "'+val+'"';
  }
  return cond
}


// Reset
// ------------
var reset_mis = function() {
  reset_values = ['module','transaction','group_by','sum_of','company','mis_type','fiscal_year','period','from_fiscal_year','to_fiscal_year','from_month','to_month','from_day','to_day'];
  for(var i = 0; i < reset_values.length ; i++){
    $i(reset_values[i]).selectedIndex = -1;
    $i(reset_values[i]).disabled = false;
  }  
  hide_options();
  get_values();
    
  // Delete Listing Object if created
  if(pscript.mis_lst){
    pscript.mis_lst.wrapper.innerHTML = '';
    delete pscript.mis_lst;
  }
}
