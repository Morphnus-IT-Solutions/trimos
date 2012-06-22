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

  # ---------
  # autoname
  # ---------
  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.####')


  # ------------------------------------------------------------------------
  # update monthly visit schedule (scheduled and unscheduled visit details)
  # ------------------------------------------------------------------------
  def update_monthly_visit_schedule(self,visit_id,actual_date,remarks,purpose,against_document_no,date):
    sql("update `tabScheduled Visit Details` set visit_report_id = %s, actual_date = %s, visit_report_remarks = %s where purpose = %s and against_document_no = %s and scheduled_date = %s",(visit_id,actual_date,remarks,purpose,against_document_no,date))
    sql("update `tabUnscheduled Visit Details` set visit_report_id = %s, actual_date = %s, visit_report_remarks = %s where purpose = %s and against_document_no = %s and scheduled_date = %s",(visit_id,actual_date,remarks,purpose,against_document_no,date))  
    

  # -------------------------
  # update lead / serial no
  # -------------------------
  def update_against_document_details(self,against_document,visit_id,actual_date,remarks,purpose,against_document_no,date):
    if against_document == 'Lead':
      sql("update `tabFollow up` set visit_report_id = %s, follow_up_actual_date = %s, remarks = %s where follow_up_status = %s and follow_up_schedule_date = %s and parent = %s",(visit_id,actual_date,remarks,purpose,date,against_document_no))
    elif against_document == 'Serial No':
      sql("update `tabService Schedule` set visit_report_id = %s, actual_date = %s, remarks = %s where service_type = %s and schedule_date = %s and parent = %s",(visit_id,actual_date,remarks,purpose,date,against_document_no))

  
  # ---------
  # validate
  # ---------
  def validate(self):
    set(self.doc, 'status', 'Open')

  
  # ----------
  # on submit
  # ----------
  def on_submit(self):
    for d in getlist(self.doclist,'visit_report_details'):
      self.update_monthly_visit_schedule(self.doc.name,d.actual_visit_start_date,self.doc.remarks_by_service_person,d.purpose,d.against_document_no,(d.scheduled_date))
      self.update_against_document_details(d.against_document,self.doc.name,d.actual_visit_start_date,self.doc.remarks_by_service_person,d.purpose,d.against_document_no,(d.scheduled_date))
    self.add_to_calendar()
    set(self.doc, 'status', 'Submitted')


  # ----------
  # on cancel
  # ----------
  def on_cancel(self):
    for d in getlist(self.doclist,'visit_report_details'):
      self.update_monthly_visit_schedule('','','',d.purpose,d.against_document_no,(d.scheduled_date))
      self.update_against_document_details(d.against_document,'','','',d.purpose,d.against_document_no,(d.scheduled_date))
    
    # Remove Events from Calendar
    sql("delete from tabEvent where ref_type = 'Visit Report' and ref_name = %s",self.doc.name)
    set(self.doc, 'status', 'Cancelled')


  # ------------------------------------
  # Add Follow Up and Date to Calendar
  # ------------------------------------
  def add_to_calendar(self):
    for d in getlist(self.doclist,'visit_report_details'):
      if d.follow_up and d.follow_up_date:
        ev = Document('Event')
        ev.description = d.follow_up
        ev.event_date = d.follow_up_date
        ev.event_hour = '10:00'
        ev.event_type = 'Private'
        ev.ref_type = self.doc.doctype
        ev.ref_name = self.doc.name
        ev.save(1)

        ch = addchild(ev, 'event_individuals', 'Event User', 0)
        ch.person = self.doc.prepared_by
        ch.save()
