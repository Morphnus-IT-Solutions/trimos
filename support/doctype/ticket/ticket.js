//filtering allocated to
cur_frm.fields_dict['allocated_to'].get_query = function(doc,cdt,cdn){
  return 'SELECT `tabProfile`.name FROM `tabProfile` WHERE `tabProfile`.user_type != "Partner" AND `tabProfile`.name LIKE "%s" ORDER BY `tabProfile`.name DESC LIMIT 50';
}

cur_frm.cscript.onload = function(doc,cdt,cdn){

  //Setting fields access
  if(has_common(user_roles,['Partner'])){
      hide_field('Allocation Details');
  }
  else{
      unhide_field('Allocation Details');
  }
  
  //if(doc.__islocal){
    //get_server_fields('sender_details','','',doc,cdt,cdn,1);
  //}
  //get response list
  if(!pscript.res_parent){
    pscript.res_parent = cur_frm.fields_dict['Response HTML'].wrapper;
    pscript.res_parent.style.margin = '0px 170px 0px 130px';
  }
  pscript.make_response_lst(doc,cdt,cdn);
}

cur_frm.cscript.refresh = function(doc,cdt,cdn) {
  if(doc.__islocal) {
//      hide_field(['Responses', 'Post', 'Response HTML', 'response']);
      doc.status = 'Open';
  }
  else {
//      unhide_field(['Responses', 'Post', 'Response HTML', 'response']);
      if(has_common(user_roles,['Partner'])){ hide_field('Allocation Details'); }
      else{ unhide_field('Allocation Details'); }
  }
  cur_frm.cscript.status(doc, cdt, cdn);
}

cur_frm.cscript.status = function(doc,cdt,cdn){
  if(doc.status == 'Closed'){
    doc.resolution_date = dateutil.obj_to_str(new Date());
    unhide_field('reason');
    refresh_field(['resolution_date', 'reason']);
  }
  else{
      doc.resolution_date = '';
      hide_field('reason');
      refresh_field(['resolution_date', 'reason']);
  }
}

//response list
pscript.make_response_lst = function(doc,cdt,cdn){
  pscript.res_parent.innerHTML = '';
  
  pscript.res_lst = new Listing('Response',1);
  pscript.res_lst.colwidths = ['100%'];
  
  pscript.res_lst.opts.hide_export = 1; pscript.res_lst.opts.hide_print = 1; pscript.res_lst.opts.hide_rec_label = 1;
  pscript.res_lst.opts.hide_refresh = 1; pscript.res_lst.opts.show_calc = 0; pscript.res_lst.opts.no_border = 1;
  
  pscript.res_lst.get_query = function(){
    this.query = repl("select response,response_by,response_date from `tabTicket Response Detail` where parent='%(doc)s' order by creation desc",{'doc':doc.name});
    this.query_max = repl("select count(response) from `tabTicket Response Detail` where parent= '%(doc)s' order by creation desc",{'doc':doc.name})
  }
  
  pscript.res_lst.show_cell = function(cell,ri,ci,d){
    res = $a(cell,'div','',{padding:'4px'});
    res.innerHTML = d[ri][0];
    
    by_date = $a(cell,'div','comment',{padding:'4px'});
    by_date.innerHTML = d[ri][1] + ' | ' + dateutil.str_to_user(d[ri][2]);

    $y(cell,{borderBottom:'1px dashed #AAA'});
  }
  
  pscript.res_lst.make(pscript.res_parent);
  pscript.res_lst.run();
  
  pscript.res_lst.onrun = function(){
    if (!pscript.res_lst.has_data()){
      pscript.res_lst.opts.hide_refresh = 1;
    }else { pscript.res_lst.opts.hide_refresh = 0;}
  }
}

//posting response
cur_frm.cscript['Post'] = function(doc,cdt,cdn){
  var callback = function(r,rt){
    doc = locals[cdt][cdn];
    doc.response = ''; refresh_field('response');
    pscript.make_response_lst(doc,cdt,cdn);
  }
  arg = {};
  arg.parent = doc.name; arg.response = doc.response; arg.response_by = user;
  $c('runserverobj',args={'method' : 'post_response','docs':compress_doclist([doc]), 'arg':docstring(arg)}, callback);
//  $c_obj('Ticket','post_response',docstring(arg),callback);
}

//cur_frm.cscript.allocated_to = function(doc,cdt,cdn){
//  get_server_fields('get_assignee_name','','',doc,cdt,cdn,1);
//}
