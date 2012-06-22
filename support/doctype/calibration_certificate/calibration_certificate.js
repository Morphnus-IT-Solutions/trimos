// --------
// refresh
// --------
cur_frm.cscript.refresh = function(doc, cdt, cdn){
  if(!doc.__islocal) unhide_field('Send for Approval');
  else hide_field('Send for Approval');
  
  if(inList(user_roles, 'CRM Manager') && !doc.__islocal) unhide_field('Send Feedback');
  else hide_field('Send Feedback');

  cur_frm.cscript.measure_x_axis(doc, cdt, cdn);
  cur_frm.cscript.measure_y_axis(doc, cdt, cdn);
  cur_frm.cscript.measure_z_axis(doc, cdt, cdn);
  cur_frm.cscript.measure_vol_axis(doc, cdt, cdn);
}


// ------------------
// serial no details
// ------------------
cur_frm.add_fetch('serial_no', 'brand', 'brand');
cur_frm.add_fetch('serial_no', 'product_code', 'product_code');


// ---------------------
// get customer details
// ---------------------
cur_frm.cscript.customer = function(doc,dt,dn) {
  var callback = function(r,rt) {
      var doc = locals[cur_frm.doctype][cur_frm.docname];
      cur_frm.refresh();
  }
  if(doc.customer) $c_obj(make_doclist(doc.doctype, doc.name), 'get_customer_details', '', callback);
}


// --------------------
// get slip id details
// --------------------
cur_frm.add_fetch('slip_id', 'type', 'type');
cur_frm.add_fetch('slip_id', 'slip_size', 'slip_size');
cur_frm.add_fetch('slip_id', 'make', 'make');
cur_frm.add_fetch('slip_id', 'self_error', 'self_error');


// Triggers for hiding and unhiding Readings tables
// --------------------------------------------------------

// X Axis
// -------- 
cur_frm.cscript.measure_x_axis = function(doc, cdt, cdn){
  if(doc.measure_x_axis == 1) unhide_field(['readings_x_axis','Readings in X Axis']);
  else hide_field(['readings_x_axis','Readings in X Axis']);
}


// Y Axis
// -------- 
cur_frm.cscript.measure_y_axis = function(doc, cdt, cdn){
  if(doc.measure_y_axis == 1) unhide_field(['readings_y_axis','Readings in Y Axis']);
  else hide_field(['readings_y_axis','Readings in Y Axis']);
}


// Z Axis
// -------- 
cur_frm.cscript.measure_z_axis = function(doc, cdt, cdn){
  if(doc.measure_z_axis == 1) unhide_field(['readings_z_axis','Readings in Z Axis']);
  else hide_field(['readings_z_axis','Readings in Z Axis']);
}


// Volumetric Axis
// ------------------
cur_frm.cscript.measure_vol_axis = function(doc, cdt, cdn){
  if(doc.measure_vol_axis == 1) unhide_field(['readings_vol_axis','Readings in Volumetric Axis']);
  else hide_field(['readings_vol_axis','Readings in Volumetric Axis']);
}

// Dictionary Of Readings Table and its Field Name
// ----------------------------------------------------
var readings_dict = {'Linear Calibration Reading':'linear_calibration_readings',
                     'Measurement Reading in X Axis':'readings_x_axis',
                     'Measurement Reading in Y Axis':'readings_y_axis',
                     'Measurement Reading in Z Axis':'readings_z_axis',
                     'Measurement Reading in Volumetric Axis':'readings_vol_axis'}
 
// Calculate Linear Calibration Readings
// --------------------------------------------------
cur_frm.cscript.slip_size = function(doc, cdt, cdn){
  calc_average(doc, cdt, cdn);
}

cur_frm.cscript.self_error = function(doc, cdt, cdn){
  calc_average(doc, cdt, cdn);
}

cur_frm.cscript.series_1 = function(doc, cdt, cdn){
  calc_average(doc, cdt, cdn);
}

cur_frm.cscript.series_2 = function(doc, cdt, cdn){
  calc_average(doc, cdt, cdn);
}

cur_frm.cscript.series_3 = function(doc, cdt, cdn){
  calc_average(doc, cdt, cdn);
}

var calc_average = function(doc, cdt, cdn){
  var d = locals[cdt][cdn];
  set_multiple(cdt, d.name, {'average': (flt(flt(d['series_1']) + flt(d['series_2']) + flt(d['series_3'])) / 3).toFixed(4)}, readings_dict[cdt]);
  var average_deviation = (flt(d.average) - (flt(d['slip_size']) + (flt(d['self_error']) / 1000))) * 1000;
  set_multiple(cdt, d.name, {'average_deviation': flt(average_deviation).toFixed(4) }, readings_dict[cdt]);
  refresh_field('average',d.name,readings_dict[cdt]);
  refresh_field('average_deviation',d.name,readings_dict[cdt]);
}
