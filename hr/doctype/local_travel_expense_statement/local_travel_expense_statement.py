# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, load_json, nowdate
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

class DocType:
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist

  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.####')


  def send_for_approval(self):
    msg = '''
Approve Local Travel Expense Statement: %s of
Employee: %s,
Prepared By: %s
''' % (self.doc.name,self.doc.employee_name, self.doc.prepared_by)
    get_obj('Sales Common').send_for_approval(self.doc.territory,msg,'Approval of Local Travel Expense Statement',self.doc.doctype,self.doc.name)
    

  def send_feedback(self):
    msg = '''
Your Local Travel Expense Statement : %s of
Employee: %s
has been Submitted
by %s
''' % (self.doc.name, self.doc.employee_name, self.doc.approved_by)
    get_obj('Sales Common').send_feedback(self.doc.employee_name,msg,'Local Travel Expense Statement status')
  
  def calculate_total_expense(self):
    total_expense = 0
    total_allowed_expense = 0
    for d in getlist(self.doclist,'local_travel_expense_details'):
      total_expense += flt(d.expense)
      total_allowed_expense += flt(d.allowed_expense)
    self.doc.total_expense = flt(total_expense)
    self.doc.total_allowed_expense = flt(total_allowed_expense)
    self.doc.total_disallowed_expense = flt(total_expense - total_allowed_expense)
    
  def validate(self):
    self.calculate_total_expense()
    self.check_late_submission()
  
  def check_late_submission(self):
    current_month = nowdate().split('-')[1]
    current_day = nowdate().split('-')[2]
    to_date_month = self.doc.end_date.split('-')[1]
    if flt(current_day) > 5 and flt(current_month) != flt(to_date_month):
      self.doc.status = 'Late'
      msgprint("Late Submission")
      if not self.doc.reason_for_late_submission:
        msgprint("Please Enter the reason for LATE Submission")
        raise Exception
    else:
      self.doc.status = 'On Time'

  def on_submit(self):
    #check whether user has permission to submit the document
    #approved_by = cstr(get_obj('Manage Account',with_children = 1).get_permissions(self.doc.doctype,self.doc.total_expense,session['user']))
    set(self.doc,'approved_by',session['user'])
