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
    self.tname = ' Service Quotation Detail'
    self.fname = 'service_quotation_details'
	# Notification objects
    self.notify_obj = get_obj('Notification Control')

  # Autoname
  # ---------
  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'.#####')

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

    
  #def get_customer_details(self, name = ''):
  #  return cstr(get_obj('Sales Common').get_customer_details(name))
  
  def get_serial_details(self, serial_no):
    return get_obj('Sales Common').get_serial_details(serial_no, self)

	# clear table
	# ------------
  def clear_service_quotation_details(self):
    self.doc.clear_table(self.doclist, 'service_quotation_details')
    
    
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


# GET TERMS AND CONDITIONS
# ====================================================================================
  def get_tc_details(self):
    return get_obj('Sales Common').get_tc_details(self)


# ------------------------------------------- utility functions -------------------------------------------------#

  def check_nextdoc_docstatus(self): 
    submit_so = sql("select t1.name from `tabService Order` t1,`tabService Order Detail` t2 where t1.name = t2.parent and t2.prevdoc_docname = '%s' and t1.docstatus = 1" % (self.doc.name))
    if submit_so:
      msgprint("Service Order : " + cstr(submit_so[0][0]) + " has been created against " + cstr(self.doc.doctype) + ". So " + cstr(self.doc.doctype) + " cannot be Cancelled.")
      raise Exception, "Validation Error."


# =========
# Validate
# =========
  # Fiscal Year Validation
  # ----------------------
  def validate_fiscal_year(self):
    get_obj('Sales Common').validate_fiscal_year(self.doc.fiscal_year,self.doc.transaction_date,'Quotation Date')
    
  # Amendment date is necessary if document is amended
  # --------------------------------------------------
  def validate_mandatory(self):
    if self.doc.amended_from and not self.doc.amendment_date:
      msgprint("Please Enter Amendment Date")
      raise Exception

  def validate_for_items(self):
    check_list=[]
    for d in getlist(self.doclist,'service_quotation_details'):
      if cstr(d.serial_no) in check_list:
        msgprint("Serial %s has been entered twice." % d.serial_no)
        raise Exception
      else:
        check_list.append(cstr(d.serial_no))

  def validate_amc_date(self):
    for d in getlist(self.doclist,'service_quotation_details'):
      if d.amc_start_date and d.amc_end_date:         # this is done coz in case type is not AMC no need to enter amc_start_date and amc_end_date
        if getdate(d.amc_start_date) >= getdate(d.amc_end_date):
          msgprint("AMC End Date must be after AMC Start Date")
          raise Exception

  def validate(self):
    self.validate_fiscal_year()
    self.validate_mandatory()
    self.validate_for_items()
    self.validate_amc_date()

    sales_com_obj = get_obj('Sales Common')
    sales_com_obj.check_conversion_rate(self)
    # Get total in words
    dcc = TransactionBase().get_company_currency(self.doc.company)
    self.doc.in_words = sales_com_obj.get_total_in_words(dcc, self.doc.rounded_total)
    self.doc.in_words_export = sales_com_obj.get_total_in_words(self.doc.currency, self.doc.rounded_total_export)    
    
 
  def on_update(self):
    # Set Quotation Status
    set(self.doc, 'status', 'Open')
    # subject for follow
    #self.doc.subject = '[%(status)s] To %(customer)s worth %(currency)s %(grand_total)s' % self.doc.fields


  def send_sms(self):
    if not self.doc.customer_mobile_no:
      msgprint("Please enter customer mobile no")
    elif not self.doc.message:
      msgprint("Please enter the message you want to send")
    else:
      msgprint(get_obj("SMS Control", "SMS Control").send_sms([self.doc.customer_mobile_no,], self.doc.message))
      
  def send_for_approval(self):
    self.doc.save()
    send_to = []
    send = sql("select t1.email from `tabProfile` t1,`tabUserRole` t2 where t2.role = 'CRM Manager' and t2.parent = t1.name")
    for d in send:
      send_to.append(d[0])
    msg = '''
Approval of Service Quotation for
Customer: %s,

''' % (self.doc.customer_name)
    sendmail(send_to, sender='automail@webnotestech.com', subject='Approval of Service Quotation', parts=[['text/plain', msg]])
    msgprint("Service Quotation has been sent for approval")

  def send_feedback(self):
    self.doc.save()
    send_to = []
    send = sql("select t1.email from `tabProfile` t1 where t1.name = %s",self.doc.owner) 
    for d in send:
      send_to.append(d[0])
    msg = '''
Service Quotation for
Customer: %s
has been Submitted
by %s

''' % (self.doc.customer_name, self.doc.approved_by)

    sendmail(send_to, sender='automail@webnotestech.com', subject='Service Quotation status', parts=[['text/plain', msg]])
    msgprint("Feedback has been sent to %s"%(self.doc.owner))
        
  def on_submit(self):
    if not self.doc.amended_from:
      set(self.doc, 'message', 'Quotation: '+self.doc.name+' has been sent')
    else:
      set(self.doc, 'message', 'Quotation has been amended. New Quotation no:'+self.doc.name)
    set(self.doc, 'status', 'Submitted')

    #check whether user has permission to submit the document
    #approved_by = cstr(get_obj('Manage Account',with_children = 1).get_permissions(self.doc.doctype,self.doc.grand_total,session['user']))
    #set(self.doc,'approved_by',approved_by)

  def on_cancel(self):
    set(self.doc, 'message', 'Quotation: '+self.doc.name+' has been cancelled')
    set(self.doc, 'status', 'Cancelled')
    self.check_nextdoc_docstatus()

  def print_other_charges(self,docname):
    print_lst = []
    for d in getlist(self.doclist,'other_charges'):
      lst1 = []
      lst1.append(d.description)
      lst1.append(d.total)
      print_lst.append(lst1)
    return print_lst
