# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, load_json, nowdate, getdate
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

class DocType:
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist

  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.####')
    
  def get_employee_details(self):
    det = sql("select department, designation, territory from `tabSales Person` where name = %s",self.doc.employee_name,as_dict = 1)
    ret = {
      'department'  :  det and det[0]['department'] or '',
      'designation'  :  det and det[0]['designation'] or '',
      'territory'  :  det and det[0]['territory'] or ''
    }
    return str(ret)

  
  def send_for_approval(self):
    msg = '''
Approve Outstation Travel Expense Statement : %s of
Employee: %s,
Prepared By: %s
''' % (self.doc.name,self.doc.employee_name, self.doc.prepared_by)
    get_obj('Sales Common').send_for_approval(self.doc.territory,msg,'Approval of Outstation Travel Expense Statement',self.doc.doctype,self.doc.name)

  def send_feedback(self):
    msg = '''
Your Outstation Travel Expense Statement for
Employee: %s
has been Submitted
by %s
''' % (self.doc.employee_name, self.doc.approved_by)
    get_obj('Sales Common').send_feedback(self.doc.employee_name,msg,'Outstation Travel Expense Statement status')

  def calculate_total_expense(self):
    total_expense = 0
    total_allowed_expense = 0
    for d in getlist(self.doclist,'travel_expense_details'):
      total_expense += flt(d.expense)
      total_allowed_expense += flt(d.allowed_expense)
    self.doc.total_expense = flt(total_expense)
    self.doc.total_allowed_expense = flt(total_allowed_expense)
    self.doc.total_disallowed_expense = flt(total_expense - total_allowed_expense)
  
  def validate(self):
    self.calculate_total_expense()
    self.check_late_submission()
  
  def check_late_submission(self):
    if (getdate(nowdate()) - getdate(self.doc.end_date)).days > 5:
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
   
    

  def get_advance(self):
    adv = sql("select allowed_amount from `tabTour Advance Requisition Slip` where name = '%s' and docstatus = 1 "%(self.doc.advance_id))
    self.doc.less_adv_rec_from = adv and flt(adv[0][0]) or 0
