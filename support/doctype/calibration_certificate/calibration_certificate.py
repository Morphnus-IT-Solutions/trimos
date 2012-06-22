import webnotes
from webnotes.utils import load_json, cint, cstr, flt, get_defaults, nowdate, getdate
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname
from webnotes.model.doclist import getlist, copy_doclist
from webnotes import msgprint

sql = webnotes.conn.sql
set = webnotes.conn.set


class DocType:
  def __init__(self,d,dl):
    self.doc, self.doclist = d,dl

  def autoname(self):
    self.doc.name = make_autoname(self.doc.product_code+'/'+self.doc.serial_no+'/'+self.doc.naming_series+'/.#')

  def get_customer_details(self):
    det = sql("select territory from tabCustomer where name = %s",self.doc.customer,as_dict = 1)
    self.doc.territory = det and det[0]['territory'] or ''
 
    addr_det = sql("select name, address_line1, address_line2, city, country, pincode, state, phone from `tabAddress` where customer = '%s' and docstatus != 2 order by is_primary_address desc limit 1" % self.doc.customer, as_dict = 1)
  
    extract = lambda x: addr_det and addr_det[0] and addr_det[0].get(x,'') or ''
    address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','phone')]
    address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
    if address_display.startswith('\n'): address_display = address_display[1:]
  
    self.doc.address = address_display


  def send_for_approval(self):
    send_to = []
    send = sql("select t1.email from `tabProfile` t1,`tabUserRole` t2 where t2.role = 'CRM Manager' and t2.parent = t1.name and ifnull(t1.enabled, 0) = 1")
    for d in send:
      send_to.append(d[0])
    msg = '''
Approve Calibration Certificate : %s

Calibrated By : %s

''' % (self.doc.name,self.doc.calibrated_by)
    sendmail(send_to, sender='automail@webnotestech.com', subject='Approval of Calibration Certificate', parts=[['text/plain', msg]])

    get_obj('Sales Common').add_to_calendar(send,msg,nowdate(),self.doc.doctype,self.doc.name)
    msgprint("Calibration Certificate sent for Approval and also added to their Calendar")


  def send_feedback(self):
    send_to = []
    send = sql("select t1.email from `tabProfile` t1 where t1.first_name = %s",self.doc.calibrated_by) 
    for d in send:
      send_to.append(d[0])
    msg = '''
Calibration Certificate : %s 
Calibrated By : %s
has been Submitted
by %s

''' % (self.doc.name, self.doc.calibrated_by, self.doc.approved_by)

    sendmail(send_to, sender='automail@webnotestech.com', subject='Calibration Certificate Status', parts=[['text/plain', msg]])
    msgprint("Feedback has been sent to '%s'"%(self.doc.calibrated_by))


  def validate(self):
    # Calculate Maximum error measured
    l = []
    for d in getlist(self.doclist,'linear_calibration_readings'):
      l.append(d.average_deviation)
    l.sort()
    self.doc.maximum_error_measured = "%.4f" %((flt(l[len(l)-1]) - flt(l[0])))
    set(self.doc, 'status', 'Open')


  def on_submit(self):
    #check whether user has permission to submit the document
    #approved_by = cstr(get_obj('Manage Account',with_children = 1).get_permissions(self.doc.doctype,'0.00',session['user']))
    #set(self.doc,'approved_by',approved_by)
    set(self.doc, 'status', 'Submitted')

    
  def on_cancel(self):
    set(self.doc, 'status', 'Cancelled')
