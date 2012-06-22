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


class DocType:
  def __init__(self,d,dl):
    self.doc, self.doclist = d, dl
    self.log = []
    
  def autoname(self):
    self.doc.name = make_autoname(self.doc.prepared_by + '/' + self.doc.naming_series + '/.##')
    
  def get_schedule(self):
    if not self.doc.month:
      msgprint("There is no month selected")
      raise Exception
    elif not self.doc.prepared_by:
      msgprint("Please select the name of the person whose schedule is to be set in Prepared By")
      raise Exception
    elif not self.doc.territory:
      msgprint("Please select the territory to get schedule")
      raise Exception
    else:
      self.doc.clear_table(self.doclist,'scheduled_visit_details')
      month_dic = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
      month = month_dic[self.doc.month]
      idx = 0
      
      # Serial No Detail
      serial_details = sql("select t1.name,t2.customer_name,t2.territory,t1.item_code,t1.brand,t1.product_code,t2.schedule_date,t2.service_type,t2.visit_report_id from `tabSerial No` t1,`tabService Schedule` t2 where MONTH(t2.schedule_date) = %s and t2.parent = t1.name and t2.territory = %s ORDER BY t2.schedule_date" ,(month,self.doc.territory), as_dict = 1)
      for s in serial_details:
        sd = addchild(self.doc, 'scheduled_visit_details', 'Scheduled Visit Details', 1, self.doclist)
        sd.customer = s['customer_name']
        sd.item_code = s['item_code']
        sd.brand = s['brand']
        sd.product_code = s['product_code']
        sd.territory = s['territory']
        sd.against_document = 'Serial No'
        sd.against_document_no = s['name']
        sd.purpose = s['service_type']
        sd.scheduled_date = s['schedule_date']
        sd.visit_report_id = s['visit_report_id']
        sd.select = 1
        sd.idx = idx
        idx += 1
        
      # Lead Details
      lead_details = sql("select t1.name,t1.customer,t1.territory,t2.item_code,t2.brand,t2.product_code,t3.follow_up_schedule_date,t3.follow_up_status,t3.visit_report_id from `tabLead` t1,`tabLead Item Detail` t2,`tabFollow up`  t3 where MONTH(t3.follow_up_schedule_date) = %s and t2.parent = t1.name and t3.parent = t1.name and t1.territory = %s and t1.docstatus = 1 ORDER BY t3.follow_up_schedule_date" ,(month,self.doc.territory), as_dict = 1)
      for l in lead_details:
        ld = addchild(self.doc, 'scheduled_visit_details', 'Scheduled Visit Details', 1, self.doclist)
        ld.customer = l['customer']
        ld.item_code = l['item_code']
        ld.brand = l['brand']
        ld.product_code = l['product_code']
        ld.territory = l['territory']
        ld.against_document = 'Lead'
        ld.against_document_no = l['name']
        ld.purpose = l['follow_up_status'] or ''
        ld.scheduled_date = l['follow_up_schedule_date'] and l['follow_up_schedule_date'] or ''
        ld.visit_report_id = l['visit_report_id']
        ld.select = 1
        ld.idx = idx
        idx += 1
        
  def get_other_details(self,args):
    args = eval(args)
    ret = {}
    
    # customer address
    details = sql("select name, address_line1, address_line2, city, country, pincode, state, phone from `tabAddress` where customer = %s and docstatus != 2 order by is_primary_address desc limit 1" , args['customer_name'], as_dict = 1)
    extract = lambda x: details and details[0] and details[0].get(x,'') or ''
    address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','phone')]
    address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
    if address_display.startswith('\n'): address_display = address_display[1:]    
   
    ret['customer_address'] = details and details[0]['name'] or ''
    ret['address_display'] = address_display
    # serial no details
    serial_details = sql("select brand,software_version,product_code from `tabSerial No` where name = %s" , args['serial_no'],as_dict = 1)
    ret['brand'] = serial_details and serial_details[0]['brand'] or ''
    ret['version'] = serial_details and serial_details[0]['software_version'] or ''
    ret['product_code'] = serial_details and serial_details[0]['product_code'] or ''
    
    # get no. of amc visits done earlier
    if args['purpose'] == 'AMC':
      no_of_visits = sql("select count(*) from `tabService Schedule` t2 where t2.service_type = 'AMC' and t2.visit_report_id is not null and t2.parent = %s",(args['serial_no']))[0][0]
      ret['amc_visit_no'] = cint(no_of_visits) + 1
    return ret

  
  def validate(self):
    set(self.doc, 'status', 'Open')

  def on_submit(self):
    #check whether user has permission to submit the document
    #approved_by = cstr(get_obj('Manage Account',with_children = 1).get_permissions(self.doc.doctype,flt(0.00),session['user']))
    #set(self.doc,'approved_by',approved_by)
    self.add_to_calendar()
    set(self.doc, 'status', 'Submitted')

  def on_cancel(self):
    sql("update tabEvent set event_type = 'Cancel' where ref_type = 'Monthly Visit Schedule' and ref_name = %s",self.doc.name)
    set(self.doc, 'status', 'Cancelled')
    
  def send_for_approval(self):
    send_to = []
    send = sql("select DISTINCT t1.email from `tabProfile` t1,`tabUserRole` t2 where t2.role = 'Schedule Approver' and t2.parent = t1.name and ifnull(t1.enabled, 0) = 1")
    territory_manager = sql("select email_id from tabTerritory where name = %s",self.doc.territory)
    send_to.append(territory_manager[0][0])
    for d in send:
      send_to.append(d[0])
    msg = '''
Approve Monthly Visit Schedule : %s
Prepared By: %s for the month of %s

''' % (self.doc.name,self.doc.prepared_by, self.doc.month)
    sendmail(send_to, sender='automail@webnotestech.com', subject='Approval of Monthly Visit Schedule', parts=[['text/plain', msg]])
    
    self.calendar_entry(send,msg,nowdate(),self.doc.doctype,self.doc.name)
    msgprint("Monthly Visit Schedule has been sent for approval")
    
  def send_feedback(self):
    self.doc.save()
    send_to = []
    send = sql("select t1.email from `tabProfile` t1 where t1.name = %s and ifnull(t1.enabled, 0) = 1",self.doc.owner) 
    for d in send:
      send_to.append(d[0])
    msg = '''
Monthly Visit Schedule of
Month : %s
has been %S
by %s

''' % (self.doc.month, self.doc.status, self.doc.approved_by)

    sendmail(send_to, sender='automail@webnotestech.com', subject='Monthly Visit Schedule Status', parts=[['text/plain', msg]])
    msgprint("Feedback has been sent to %s"%(self.doc.owner))


  def add_to_calendar(self):
    send = sql('select email_id from `tabSales Person` where name = %s',self.doc.prepared_by)
    for d in getlist(self.doclist,'scheduled_visit_details'):
      message = '''Purpose : %s for Customer : %s'''%(d.purpose,d.customer_name)
      self.calendar_entry(send,message,d.scheduled_date,self.doc.doctype,self.doc.name)

    for d in getlist(self.doclist,'unscheduled_visit_details'):
      message = '''Purpose : %s for Customer : %s'''%(d.purpose,d.customer_name)
      self.calendar_entry(send,message,d.scheduled_date,self.doc.doctype,self.doc.name)


  def calendar_entry(self, send, message, date, doctype, name):
    ev = Document('Event')
    ev.description = message
    ev.event_date = date
    ev.event_hour = '10:00'
    ev.event_type = 'Private'
    ev.ref_type = doctype
    ev.ref_name = name
    ev.save(1)

    for d in send: 
      ch = addchild(ev, 'event_individuals', 'Event User', 0)
      ch.person = d[0]
      ch.save()
