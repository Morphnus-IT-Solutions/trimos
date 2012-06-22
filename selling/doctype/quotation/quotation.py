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
    self.tname = 'Quotation Detail'
    self.fname = 'quotation_details'
    
    # Notification objects
    self.notify_obj = get_obj('Notification Control')

  # Autoname
  # ---------
  def autoname(self):
    #self.doc.name = make_autoname(self.doc.naming_series+'.#####')
    # custom autoname
    if self.doc.sub_category == 'INR':
      self.doc.name = make_autoname(cstr(self.doc.supplier_name)+'/'+self.doc.naming_series+'/I/.####')
    elif self.doc.sub_category == 'DI':
      self.doc.name = make_autoname(cstr(self.doc.supplier_name)+'/'+self.doc.naming_series+'/D/.####')


# DOCTYPE TRIGGER FUNCTIONS
# ==============================================================================    
 
  # Pull Enquiry Details
  # --------------------
  def pull_enq_details(self):
    self.doc.clear_table(self.doclist, 'quotation_details')
    get_obj('DocType Mapper', 'Enquiry-Quotation').dt_map('Enquiry', 'Quotation', self.doc.enq_no, self.doc, self.doclist, "[['Enquiry', 'Quotation'],['Enquiry Detail', 'Quotation Detail']]")

    self.get_adj_percent()

    return self.doc.quotation_to

  # Get contact person details based on customer selected
  # ------------------------------------------------------
  def get_contact_details(self):
    return get_obj('Sales Common').get_contact_details(self,0)
  
  # Clear Quotation Details
  # -----------------------
  def clear_quotation_details(self):
    self.doc.clear_table(self.doclist, 'quotation_details')  
  
    
# QUOTATION DETAILS TRIGGER FUNCTIONS
# ================================================================================    

  # Get Item Details
  # -----------------
  def get_item_details(self, item_code):
    return get_obj('Sales Common').get_item_details(item_code, self)
  
  # Re-calculates Basic Rate & amount based on Price List Selected
  # --------------------------------------------------------------
  def get_adj_percent(self, arg=''):
    get_obj('Sales Common').get_adj_percent(self)
    

# OTHER CHARGES TRIGGER FUNCTIONS
# ====================================================================================
  
  # Get Tax rate if account type is TAX
  # -----------------------------------
  def get_rate(self,arg):
    return get_obj('Sales Common').get_rate(arg)

  # Load Default Charges
  # ----------------------------------------------------------
  def load_default_taxes(self):
    return get_obj('Sales Common').load_default_taxes(self)

  # Pull details from other charges master (Get Other Charges)
  # ----------------------------------------------------------
  def get_other_charges(self):
    return get_obj('Sales Common').get_other_charges(self)
  
  # Get Lead Details along with its details
  # ==============================================================
#  def get_lead_details1(self, name):    
#    details = sql("select name, lead_name, company_name, address_line1, address_line2, city, country, state, pincode, territory, contact_no, mobile_no, email_id from `tabLead` where name = '%s'" %(name), as_dict = 1)   
#    ret = {
#      'lead_name' : details and details[0]['lead_name'] or '',
#      'company_name': details and details[0]['company_name'] or '',
#      'address_display' : (details and details[0]['address_line1']
#				     + (details[0]['address_line2'] and '\n' + details[0]['address_line2'] or '') + '\n' 
#				     + details[0]['city'] 
#				     + (details[0]['pincode'] and ', ' + details[0]['pincode'] or '') + '\n' 
#				     + (details[0]['state'] and details[0]['state']+', ' or '') 
#				     + details[0]['country'] + '\nTel: ' + details[0]['contact_no'] + '\n' or '-'),
#      'territory' : details and details[0]['territory'] or '',
#      'contact_mobile' : details and details[0]['mobile_no'] or '-',
#      'contact_email' : details and details[0]['email_id'] or '-'      
#    }
#    return ret
  # -------------------------------
  # get lead details (Overwritten)
  # -------------------------------
  def get_lead_details1(self):
#    details = sql("select name, lead_name, transaction_date, customer_group, address_line1, address_line2, city, country, state, pincode, territory, contact_no, mobile_no, email_id, customer, company_name, zone, department, designation from `tabLead` where name = '%s'" %(name), as_dict = 1)
#    extract = lambda x: details and details[0] and details[0].get(x,'') or ''
#    address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','contact_no')]
#    address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
#    if address_display.startswith('\n'): address_display = address_display[1:]
#    ret = {
#      'customer' : extract('customer'),
#      'customer_name' : extract('company_name'),
#      'customer_group' : extract('customer_group'),
#      'lead_name' : extract('company_name'),
#      'lead_date' : extract('transaction_date'),
#      'territory' : extract('territory'),
#      'zone' : extract('zone'),
#      'contact_display' : extract('lead_name'),
#      'address_display' : address_display,
#      'territory' : extract('territory'),
#      'contact_mobile' : extract('mobile_no'),
#      'contact_email' : extract('email_id'),
#      'contact_department' : extract('department'),
#      'contact_designation' : extract('designation')
#    }
#    return ret
    self.doc.clear_table(self.doclist, 'quotation_details')
    get_obj('DocType Mapper', 'Lead-Quotation').dt_map('Lead', 'Quotation', self.doc.lead, self.doc, self.doclist, "[['Lead', 'Quotation'],['Lead Item Detail', 'Quotation Detail']]")			

     
# GET TERMS AND CONDITIONS
# ====================================================================================
  def get_tc_details(self):
    return get_obj('Sales Common').get_tc_details(self)

    
# VALIDATE
# ==============================================================================================
  
  # Amendment date is necessary if document is amended
  # --------------------------------------------------
  def validate_mandatory(self):
    if self.doc.amended_from and not self.doc.amendment_date:
      msgprint("Please Enter Amendment Date")
      raise Exception

  # Fiscal Year Validation
  # ----------------------
  def validate_fiscal_year(self):
    get_obj('Sales Common').validate_fiscal_year(self.doc.fiscal_year,self.doc.transaction_date,'Quotation Date')
  
  # Does not allow same item code to be entered twice
  # -------------------------------------------------
  def validate_for_items(self):
    check_list=[]
    chk_dupl_itm = []
    for d in getlist(self.doclist,'quotation_details'):
      ch = sql("select is_stock_item from `tabItem` where name = '%s'"%d.item_code)
      if ch and ch[0][0]=='Yes':
        if cstr(d.item_code) in check_list:
	  msgprint("Item %s has been entered twice." % d.item_code)
	  raise Exception
	else:
	  check_list.append(cstr(d.item_code))
      
      if ch and ch[0][0]=='No':
        f = [cstr(d.item_code),cstr(d.description)]
	if f in chk_dupl_itm:
	  msgprint("Item %s has been entered twice." % d.item_code)
	  raise Exception
	else:
	  chk_dupl_itm.append(f)


  #do not allow sales item in maintenance quotation and service item in sales quotation
  #-----------------------------------------------------------------------------------------------
  def validate_order_type(self):
    if self.doc.order_type == 'Maintenance':
      for d in getlist(self.doclist, 'quotation_details'):
        is_service_item = sql("select is_service_item from `tabItem` where name=%s", d.item_code)
        is_service_item = is_service_item and is_service_item[0][0] or 'No'
        
        if is_service_item == 'No':
          msgprint("You can not select non service item "+d.item_code+" in Maintenance Quotation")
          raise Exception
    else:
      for d in getlist(self.doclist, 'quotation_details'):
        is_sales_item = sql("select is_sales_item from `tabItem` where name=%s", d.item_code)
        is_sales_item = is_sales_item and is_sales_item[0][0] or 'No'
        
        if is_sales_item == 'No':
          msgprint("You can not select non sales item "+d.item_code+" in Sales Quotation")
          raise Exception
  
  #--------------Validation For Last Contact Date-----------------
  # ====================================================================================================================
  def set_last_contact_date(self):
    #if not self.doc.contact_date_ref:
      #self.doc.contact_date_ref=self.doc.contact_date
      #self.doc.last_contact_date=self.doc.contact_date_ref
    if self.doc.contact_date and self.doc.contact_date_ref and self.doc.contact_date_ref != self.doc.contact_date:
      if getdate(self.doc.contact_date_ref) < getdate(self.doc.contact_date):
        self.doc.last_contact_date=self.doc.contact_date_ref
      else:
        msgprint("Contact Date Cannot be before Last Contact Date")
        raise Exception
      #set(self.doc, 'contact_date_ref',self.doc.contact_date)
  

  # Validate
  # --------
  def validate(self):
    self.validate_fiscal_year()
    self.validate_mandatory()
    self.set_last_contact_date()
    self.validate_order_type()
    self.validate_for_items()
    sales_com_obj = get_obj('Sales Common')
    sales_com_obj.validate_max_discount(self,'quotation_details') #verify whether rate is not greater than max_discount
    sales_com_obj.check_conversion_rate(self)
    
    # Get total in words
    dcc = TransactionBase().get_company_currency(self.doc.company)
    self.doc.in_words = sales_com_obj.get_total_in_words(dcc, self.doc.rounded_total)
    self.doc.in_words_export = sales_com_obj.get_total_in_words(self.doc.currency, self.doc.rounded_total_export)

  def on_update(self):
    # Add to calendar
    #if self.doc.contact_date and self.doc.last_contact_date != self.doc.contact_date:
    if self.doc.contact_date and self.doc.contact_date_ref != self.doc.contact_date:
      if self.doc.contact_by:
        self.add_calendar_event()
      set(self.doc, 'contact_date_ref',self.doc.contact_date)
    
    # Set Quotation Status
    set(self.doc, 'status', 'Draft')

    # subject for follow
    #self.doc.subject = '[%(status)s] To %(customer)s worth %(currency)s %(grand_total)s' % self.doc.fields

  
  # Add to Calendar
  # ====================================================================================================================
  def add_calendar_event(self):
    desc=''
    user_lst =[]
    if self.doc.customer:
      if self.doc.contact_person:
        desc = 'Contact '+cstr(self.doc.contact_person)
      else:
        desc = 'Contact customer '+cstr(self.doc.customer)
    elif self.doc.lead:
      if self.doc.lead_name:
        desc = 'Contact '+cstr(self.doc.lead_name)
      else:
        desc = 'Contact lead '+cstr(self.doc.lead)
    desc = desc+ '.By : ' + cstr(self.doc.contact_by)
    
    if self.doc.to_discuss:
      desc = desc+' To Discuss : ' + cstr(self.doc.to_discuss)
    
    ev = Document('Event')
    ev.description = desc
    ev.event_date = self.doc.contact_date
    ev.event_hour = '10:00'
    ev.event_type = 'Private'
    ev.ref_type = 'Enquiry'
    ev.ref_name = self.doc.name
    ev.save(1)
    
    user_lst.append(self.doc.owner)
    
    chk = sql("select t1.name from `tabProfile` t1, `tabSales Person` t2 where t2.email_id = t1.name and t2.name=%s",self.doc.contact_by)
    if chk:
      user_lst.append(chk[0][0])
    
    for d in user_lst:
      ch = addchild(ev, 'event_individuals', 'Event User', 0)
      ch.person = d
      ch.save(1)
  
  #update enquiry
  #------------------
  def update_enquiry(self, flag):
    prevdoc=''
    for d in getlist(self.doclist, 'quotation_details'):
      if d.prevdoc_docname:
        prevdoc = d.prevdoc_docname
    
    if prevdoc:
      if flag == 'submit': #on submit
        sql("update `tabEnquiry` set status = 'Quotation Sent' where name = %s", prevdoc)
      elif flag == 'cancel': #on cancel
        sql("update `tabEnquiry` set status = 'Open' where name = %s", prevdoc)
      elif flag == 'order lost': #order lost
        sql("update `tabEnquiry` set status = 'Enquiry Lost' where name=%s", prevdoc)
      elif flag == 'order confirm': #order confirm
        sql("update `tabEnquiry` set status='Order Confirmed' where name=%s", prevdoc)
  
  # declare as order lost
  #-------------------------
  def declare_order_lost(self,arg):
    chk = sql("select t1.name from `tabSales Order` t1, `tabSales Order Detail` t2 where t2.parent = t1.name and t1.docstatus=1 and t2.prevdoc_docname = %s",self.doc.name)
    if chk:
      msgprint("Sales Order No. "+cstr(chk[0][0])+" is submitted against this Quotation. Thus 'Order Lost' can not be declared against it.")
      raise Exception
    else:
      set(self.doc, 'status', 'Order Lost')
      set(self.doc, 'order_lost_reason', arg)
      self.update_enquiry('order lost')
      return 'true'
  
  #check if value entered in item table
  #--------------------------------------
  def check_item_table(self):
    if not getlist(self.doclist, 'quotation_details'):
      msgprint("Please enter item details")
      raise Exception

  def update_lead_status(self, status):
    if self.doc.lead:
      sql("update tabLead set status = '%s', modified = '%s' where name = '%s'" % (status, nowdate(), self.doc.lead))    


  # ON SUBMIT
  # =========================================================================
  def on_submit(self):
    self.check_item_table()
    if not self.doc.amended_from:
      set(self.doc, 'message', 'Quotation: '+self.doc.name+' has been sent')
    else:
      set(self.doc, 'message', 'Quotation has been amended. New Quotation no:'+self.doc.name)
    
    # Check for Approving Authority
    get_obj('Authorization Control').validate_approving_authority(self.doc.doctype, self.doc.company, self.doc.grand_total, self)

    # Set Quotation Status
    set(self.doc, 'status', 'Submitted')
    
    #update enquiry status
    self.update_enquiry('submit')

    # update lead status
    self.update_lead_status('Quotation Given')
    
    # on submit notification
    self.notify_obj.notify_contact('Quotation', self.doc.doctype, self.doc.name, self.doc.email_id, self.doc.contact_person)

    
# ON CANCEL
# ==========================================================================
  def on_cancel(self):
    set(self.doc, 'message', 'Quotation: '+self.doc.name+' has been cancelled')
    
    #update enquiry status
    self.update_enquiry('cancel')

    # update lead status
    self.update_lead_status('Open')    

    set(self.doc,'status','Cancelled')
    
  
# SEND SMS
# =============================================================================
  def send_sms(self):
    if not self.doc.customer_mobile_no:
      msgprint("Please enter customer mobile no")
    elif not self.doc.message:
      msgprint("Please enter the message you want to send")
    else:
      msgprint(get_obj("SMS Control", "SMS Control").send_sms([self.doc.contact_mobile,], self.doc.message))
  
# Print other charges
# ===========================================================================
  def print_other_charges(self,docname):
    print_lst = []
    for d in getlist(self.doclist,'other_charges'):
      lst1 = []
      lst1.append(d.description)
      lst1.append(d.total)
      print_lst.append(lst1)
    return print_lst
  
  def update_followup_details(self):
    sql("delete from `tabFollow up` where parent = '%s'"%self.doc.name)
    for d in getlist(self.doclist, 'follow_up'):
      d.save()
