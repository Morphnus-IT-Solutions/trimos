import webnotes
from webnotes.utils import load_json, cint, cstr, flt, get_defaults, nowdate, getdate
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname
from webnotes.model.doclist import getlist, copy_doclist
from webnotes import msgprint, session
from webnotes.model.code import get_obj

sql = webnotes.conn.sql
set = webnotes.conn.set


class DocType:
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist

  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.####')


  def send_for_approval(self):
    msg = '''
Approval of Tour Advance Requisition Slip of
Employee: %s
''' % (self.doc.employee_name)
    get_obj('Sales Common').send_for_approval(self.doc.territory,msg,'Approval of Tour Advance Requisition Slip',self.doc.doctype,self.doc.name)
    

  def send_feedback(self):
    msg = '''
Your Tour Advance Requisition Slip for
Employee: %s
has been %s
by %s
''' % (self.doc.employee_name, self.doc.status, self.doc.approved_by)
    get_obj('Sales Common').send_feedback(self.doc.employee_name,msg,'Tour Advance Requisition Slip status')

  
  def validate(self):
    set(self.doc, 'status', 'Open')

  
  def on_submit(self):
    #check whether user has permission to submit the document
    #approved_by = cstr(get_obj('Manage Account',with_children = 1).get_permissions(self.doc.doctype,self.doc.total,session['user']))
    approved_by = sql("select first_name, last_name from `tabProfile` where name = '%s'" % session['user'])
    fst_nm = approved_by and approved_by[0][0] or ''
    lst_nm = approved_by and approved_by[0][1] or ''
    if fst_nm and lst_nm :
      approver_nm = fst_nm + " " + lst_nm
    elif fst_nm :
      approver_nm = fst_nm
    set(self.doc,'approved_by',str(approver_nm))
    set(self.doc, 'status', 'Submitted')


  def on_cancel(self):
    set(self.doc, 'status', 'Cancelled')

    
  def update_amount(self):
    self.doc.save()
