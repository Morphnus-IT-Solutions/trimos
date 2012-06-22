import webnotes
from webnotes.utils import load_json, cint, cstr, flt, get_defaults, nowdate, getdate
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname
from webnotes.model.doclist import getlist, copy_doclist
from webnotes import msgprint

sql = webnotes.conn.sql
set = webnotes.conn.set

from utilities.transaction_base import TransactionBase

class DocType(TransactionBase):
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist

  def autoname(self):
    self.doc.name = make_autoname(self.doc.serial_no+'/'+self.doc.purpose+'/'+self.doc.naming_series+'/.##')

    
  def update_monthly_visit_schedule(self,visit_id,actual_date,remarks):
    sql("update `tabScheduled Visit Details` set visit_report_id = %s, actual_date = %s, visit_report_remarks = %s where purpose = %s and against_document_no = %s and scheduled_date = %s",(visit_id,actual_date,remarks,self.doc.purpose,self.doc.serial_no,getdate(self.doc.scheduled_date)))
    sql("update `tabUnscheduled Visit Details` set visit_report_id = %s, actual_date = %s, visit_report_remarks = %s where purpose = %s and against_document_no = %s and scheduled_date = %s",(visit_id,actual_date,remarks,self.doc.purpose,self.doc.serial_no,getdate(self.doc.scheduled_date)))
    
  def update_against_document_details(self,visit_id,actual_date,remarks):
    sql("update `tabService Schedule` set visit_report_id = %s, actual_date = %s, remarks = %s where service_type = %s and schedule_date = %s and parent = %s",(visit_id,actual_date,remarks,self.doc.purpose,getdate(self.doc.scheduled_date),self.doc.serial_no))


  def validate(self):
    set(self.doc, 'status', 'Open')    

  def on_submit(self):
    if self.doc.scheduled_date:
      self.update_monthly_visit_schedule(self.doc.name,getdate(self.doc.report_date),self.doc.remark_by_engineer)
      self.update_against_document_details(self.doc.name,getdate(self.doc.report_date),self.doc.remarks_by_engineer)
    set(self.doc, 'status', 'Submitted')
    self.add_calendar_event(self.doc.further_action_to_be_taken_by,self.doc.action_plan,self.doc.target_date_of_completion)
    
  def on_cancel(self):
    self.update_monthly_visit_schedule('','','')
    self.update_against_document_details('','','')
    set(self.doc, 'status', 'Cancelled')
    
  def add_calendar_event(self,further_action,action,date):
    ev = Document('Event')
    ev.description = 'Further Action To Be Taken : ' + cstr(further_action) + ' by ' + cstr(action)
    ev.event_date = date
    ev.event_hour = '10:00'
    ev.event_type = 'Public'
    ev.ref_type = 'Service Report'
    ev.ref_name = self.doc.name
    ev.save(1)
      
    user_list=['CRM Manager', 'Service Team']
    for d in user_list:
      ch = addchild(ev, 'event_roles', 'Event Role', 0)
      ch.role = d
      ch.save()
      
    msgprint("Schedule added to Calendar")
      
  def remove_calendar_event(self):
    sql("update tabEvent set event_type = 'Cancel' where ref_type = 'Service Report' and ref_name = '%s'" % self.doc.name)
    msgprint("Schedule Cancelled from Calendar")
