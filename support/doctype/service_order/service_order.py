# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, getdate, has_common, month_name, now, nowdate, replace_newlines, sendmail, set_default, str_esc_quote, user_format, validate_email_add
from webnotes.model import db_exists
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname, SuperDocType
from webnotes.model.doclist import getlist, copy_doclist
from webnotes.model.code import get_obj, get_server_obj, run_server_obj, updatedb, check_syntax
from webnotes import session, form, is_testing, msgprint, errprint

set = webnotes.conn.set
sql = webnotes.conn.sql
get_value = webnotes.conn.get_value
in_transaction = webnotes.conn.in_transaction
convert_to_lists = webnotes.conn.convert_to_lists

# -----------------------------------------------------------------------------------------


from utilities.transaction_base import TransactionBase

class DocType(TransactionBase):
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist
    self.tname = 'Service Order Detail'
    self.fname = 'service_order_details'
    # Notification objects
    self.notify_obj = get_obj('Notification Control')

  # ---------
  # autoname
  # ---------
  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.####')
  

  def get_serial_details(self, serial_no):
    return get_obj('Sales Common').get_serial_details(serial_no, self)


#---------------- get tax rate if account type is tax  (Trigger written in other charges master)----------------------------#
   
  def get_rate(self,arg):
    get_obj('Other Charges').get_rate(arg)

#--------------------- pull details from other charges master (Get Other Charges) ---------------------------------#

  def get_other_charges(self):
    return get_obj('Sales Common').get_other_charges(self)

#------------------------------------- Get Terms and Conditions -----------------------------------------------#

  def get_tc_details(self):
    self.doc.clear_table(self.doclist,'tc_details')
    tc_detail = sql("select terms,description from `tabTC Detail` where parent = '%s'" %(self.doc.tc_name), as_dict = 1)
    for tc in tc_detail:
      d =  addchild(self.doc, 'tc_details', 'TC Detail', 1, self.doclist)
      d.terms = tc['terms']
      d.description = tc['description']

    
  #------------------------------------------------------------------------------------------
  #trigger functions
  def pull_service_quotation_details(self):
    self.doc.clear_table(self.doclist, 'other_charges')
    self.doc.clear_table(self.doclist, 'service_order_details')
    self.doc.clear_table(self.doclist, 'sales_team')
    get_obj('DocType Mapper', 'Service Quotation-Service Order').dt_map('Service Quotation', 'Service Order', self.doc.service_quotation_no, self.doc, self.doclist, "[['Service Quotation', 'Service Order'],['Service Quotation Detail', 'Service Order Detail'], ['RV Tax Detail', 'RV Tax Detail'],['Sales Team','Sales Team']]")

  def clear_service_order_details(self):
    self.doc.clear_table(self.doclist, 'service_order_details')

  #-------------------------------------------------------------------------------------------
  #Validation
  def validate_mandatory(self):
    if self.doc.amended_from and not self.doc.amendment_date:
      msgprint("Please Enter Amendment Date")
      raise Exception

    
#---------------------------------- server side functions ----------------------------------------------------#
  
  def validate_for_items(self):
    check_list=[]
    for d in getlist(self.doclist,'service_order_details'):
      if cstr(d.serial_no) in check_list:
        msgprint("Serial %s has been entered twice." % d.serial_no)
        raise Exception
      else:
        check_list.append(cstr(d.serial_no))

  def validate_amc_date(self):
    for d in getlist(self.doclist,'service_order_details'):
      if d.start_date and d.end_date:      # in AMC we don't require start_date and end_date
        if getdate(d.start_date) >= getdate(d.end_date):
          msgprint("End Date must be after Start Date in Item .")
          raise Exception
        if flt(d.no_of_visit) <= 0:
          msgprint("No of visit must be a positive value")
          raise Exception

  def validate(self):
    set(self.doc, 'status', 'Open')
    self.validate_mandatory()
    self.validate_for_items()
    self.validate_amc_date()
    #****************************** get total in words **************************************************#
    self.doc.in_words = get_obj('Sales Common').get_total_in_words('Rs', flt(self.doc.rounded_total))
    self.doc.in_words_export = get_obj('Sales Common').get_total_in_words(self.doc.currency, flt(self.doc.rounded_total_export))
    
  def update_lead_status(self, st):
    if self.doc.inquiry_no:
      if st == 'Confirm' : status = 'Order Confirmed'
      elif st == 'Cancel' and sql("select name from `tabService Quotation` where inquiry_no = '%s'" % (self.doc.inquiry_no)): status = 'Quotation Given'
      else: st = 'Open'
      sql("update `tabLead` set status = '%s' where name = '%s'" % (status, self.doc.inquiry_no))
        
  def update_warranty_amc_history(self, submit = 1):
    if self.doc.order_type in ['AMC', 'OTS (One Time Service)']:
      sr_list = []
      if submit:
        for d in getlist(self.doclist, 'service_order_details'):
          sr = Document('Serial No', d.serial_no)
          child = addchild(sr, 'warranty_amc_history', 'Warranty AMC History', 0)
          child.from_date = d.start_date
          child.to_date = d.end_date
          child.status = (self.doc.order_type == 'AMC') and 'Under AMC' or 'OTS (One Time Service)'
          child.against_doctype = self.doc.doctype
          child.against_docname = self.doc.name
          child.customer = self.doc.customer
          child.territory = self.doc.territory
          child.save()
          sr.warranty_amc_status = (self.doc.order_type == 'AMC') and 'Under AMC' or 'OTS (One Time Service)'
          sr.amc_expiry_date = d.end_date
          sr.save()
          sr_list.append(d.serial_no)
      else:
        sql("delete from `tabWarranty AMC History` where against_doctype = %s and against_docname = %s", (self.doc.doctype, self.doc.name))
        for d in getlist(self.doclist, 'service_order_details'):
          sql("update `tabSerial No` set amc_expiry_date = '' where name = '%s'" % (d.serial_no))
          sr_list.append(d.serial_no)
      self.update_serial_no_warranty_amc_status(serial_no_list = sr_list)
        
  def on_submit(self):
    set(self.doc, 'status', 'Submitted')
    # Update Lead
    self.update_lead_status('Confirm')
    self.update_serial_master()
    self.update_warranty_amc_history(submit = 1)
    msgprint("Schedule added to calender")


  def on_cancel(self):
    set(self.doc, 'status', 'Cancelled')
    self.update_lead_status('Cancel')
    # remove from calendar and serial master
    self.remove_from_serial_table()
    self.update_warranty_amc_history(submit = 0)
    self.remove_calendar_event()


  def print_other_charges(self,docname):
    print_lst = []
    for d in getlist(self.doclist,'other_charges'):
      lst1 = []
      lst1.append(d.description)
      lst1.append(d.total)
      print_lst.append(lst1)
    return print_lst
  
  # ----------------------Add service schedule in serial Master---------------------------------
  
  def update_serial_master(self):
    import datetime
    for d in getlist(self.doclist,'service_order_details'):
      if d.no_of_visit == 1:
        self.add_to_serial_table(d.serial_no,d.start_date)
      else :
        st_dt = getdate(d.start_date)
        end_dt = getdate(d.end_date)
        if d.no_of_visit > 0:
          days = cint(((end_dt - st_dt).days)/d.no_of_visit)  # this gives the period between two visits
        schedule_list = []
        for no in range(cint(d.no_of_visit)):
          if (getdate(str(st_dt)) < getdate(str(end_dt))):
            sch_dt = add_days(str(st_dt), days)
            schedule_list.append(sch_dt)
            st_dt = sch_dt
        for sl in range (len(schedule_list)):
          self.add_to_serial_table(d.serial_no,schedule_list[sl])
    
  def add_to_serial_table(self,ser_no,sch_dt):
    serial_list = Document('Serial No',ser_no)
    child = addchild(serial_list, 'service_schedule', 'Service Schedule', 0)
    child.schedule_date = sch_dt
    child.customer_name = self.doc.customer_name
    child.territory = self.doc.territory
    child.service_type = self.doc.order_type
    child.against_docname = self.doc.name
    child.save()
    self.add_calendar_event(ser_no,sch_dt,self.doc.order_type)
    
  def add_calendar_event(self,ser_no,sch_dt,service):
    ev = Document('Event')
    ev.description = cstr(ser_no) + '/' + cstr(service)
    ev.event_date = sch_dt
    ev.event_hour = '10:00'
    ev.event_type = 'Private'
    ev.ref_type = 'Service Order'
    ev.ref_name = self.doc.name
    ev.save(1)
      
    user_list=['CRM Manager', 'CRM User', 'CRM - Back Office']
    for d in user_list:
      ch = addchild(ev, 'event_roles', 'Event Role', 0)
      ch.role = d
      ch.save()

  def remove_from_serial_table(self):
    sql("delete from `tabService Schedule` where against_docname = %s",self.doc.name)

  def remove_calendar_event(self):
    sql("update tabEvent set event_type = 'Cancel' where ref_type = 'Service Order' and ref_name = '%s'" % self.doc.name)
    msgprint("Schedule Cancelled from calendar")
