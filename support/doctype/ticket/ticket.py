
# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, load_json, nowdate
from webnotes.model import db_exists
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname, SuperDocType
from webnotes.model.doclist import getlist, copy_doclist
from webnotes.model.code import get_obj, get_server_obj, run_server_obj, updatedb, check_syntax
from webnotes import session, form, is_testing, msgprint, errprint
from webnotes.utils.email_lib import sendmail
set = webnotes.conn.set
sql = webnotes.conn.sql
get_value = webnotes.conn.get_value
in_transaction = webnotes.conn.in_transaction
convert_to_lists = webnotes.conn.convert_to_lists

email_header = '''
<html>
  <body style="background-color: #EEE; padding: 10px; font-family: Arial">
  <style>table.border_tab td { background-color: #FFF; border: 1px solid #CCC; padding: 10px }</style>
  <div>
    <h3>Ticket %s : %s</h3>
  <table style="width:90%%; border-collapse: collapse;" class="border_tab">
'''

email_footer = '''
</table>
</div><br>
To login in the system, use link : <div><a href='http://cimworks.in/' target='_blank'>http://cimworks.in</a></div><br><br>

<div style='padding:16px;'>
<hr><br>
<span>Trimos Metrology India Pvt. Ltd.</span><br>
<span><a href='http://www.trimosmetrology.net' target='_blank'>www.trimosmetrology.net</a></span>
</div>
</body>
</html>
'''
class DocType:
  def __init__(self,doc,doclist=[]):
    self.doc = doc
    self.doclist = doclist
    
  def sender_details(self):
    sd = sql("select concat_ws(' ', first_name, ifnull(last_name,'')) ,name  from `tabProfile` where name=%s",session['user'])
    ret = {
     'senders_name'  : sd and sd[0][0] or '',
      'senders_email' : sd and sd[0][1] or '',
    }
    return cstr(ret)

  def get_name(self, name):
    sd = sql("select concat_ws(' ', first_name, ifnull(last_name,'')) ,name  from `tabProfile` where name=%s",name)
    senders_name = sd and cstr(sd[0][0]) or ''
    return senders_name

      
  def get_close_ticket_summary(self):
    t = """
<tr><td>Resolved By:</td><td> %s</td></tr>
<tr><td>Resolution Details:</td><td> %s</td></tr>
<tr><td>Status:</td><td> %s</td></tr>
<tr><td>Resolution Date:</td><td> %s</td></tr>
""" % (self.get_name(self.doc.allocated_to), self.doc.reason, self.doc.status, self.doc.resolution_date)
    	
    email = email_header % (self.doc.name,self.doc.subject) + t + email_footer
    return email
    
  def get_open_ticket_summary(self):
    t = """
<tr><td>Sender's Name:</td><td> %s</td></tr>
<tr><td>Subject:</td><td> %s</td></tr>
<tr><td>Description:</td><td> %s</td></tr>
<tr><td>Status:</td><td> %s</td></tr>
<tr><td>Priority:</td><td> %s</td></tr>
<tr><td>Type:</td><td> %s</td></tr>
<tr><td>Scheduled Date:</td><td> %s</td></tr>
""" % (self.get_name(self.doc.senders_email), self.doc.subject, self.doc.description, self.doc.status, self.doc.priority, self.doc.type, self.doc.scheduled_date)

    email = email_header % (self.doc.name,self.doc.subject) + t + email_footer
    return email
    
  def get_allocated_ticket_summary(self):
    t = """
<tr><td>Sender's Name:</td><td> %(senders_name)s</td></tr>
<tr><td>Sender's Company:</td><td> %(senders_company)s</td></tr>
<tr><td>Priority:</td><td> %(priority)s</td></tr>
<tr><td>Subject:</td><td> %(subject)s</td></tr>
<tr><td>Description:</td><td> %(description)s</td></tr>
<tr><td>Status:</td><td> %(status)s</td></tr>
<tr><td>Scheduled Date:</td><td> %(scheduled_date)s</td></tr>
""" % (self.doc.fields)

    email = email_header % (self.doc.name,self.doc.subject) + t + email_footer
    return email
    
  def get_response_summary(self,response_by,response):
  
    t = """
<tr><td>Subject:</td><td> %s</td></tr>
<tr><td>Description:</td><td> %s</td></tr>
<tr><td>Response:</td><td> %s</td></tr>
<tr><td>Response By:</td><td> %s</td></tr>
""" % (self.doc.subject,self.doc.description,response,response_by)

    email = email_header % (self.doc.name,self.doc.subject) + t + email_footer
    return email

  def validate(self):
    if not self.doc.senders_email:
      msgprint('Please enter valid Senders Email')
      raise Exception
      
    if self.doc.resolution_date and self.doc.status != 'Closed':
      msgprint("You can enter Resolution Date only if Status is Closed")
      self.doc.resolution_date = ''
      raise Exception

    if self.doc.status == 'Closed' and not (self.doc.resolution_date or self.doc.reason):
      msgprint("Please enter resolution date and resolution details")
      raise Exception
  
 
  def on_update(self):
    if self.doc.status == 'Open':
      email = []
      if self.doc.allocated_to in ['dalal.saumil@gmail.com', 'chintan.saglani@gmail.com']:
        email = ['dalal.saumil@gmail.com', 'chintan.saglani@gmail.com']
      else:
        email = [self.doc.allocated_to]
       
      sendmail(email, self.doc.senders_email, subject = 'New Ticket: %s, %s' % (self.doc.name, self.doc.subject) or '', parts = [['text/html',self.get_open_ticket_summary() or '']], cc = ['sangeeta_a@trimosmetrology.net', 'manisha_s@trimosmetrology.net'])
    elif self.doc.status == 'Closed':
      email_cc = []
      if self.doc.allocated_to in ['dalal.saumil@gmail.com', 'chintan.saglani@gmail.com']:
        email_cc = ['dalal.saumil@gmail.com', 'chintan.saglani@gmail.com']
      else:
        email_cc = ['sangeeta_a@trimosmetrology.net', 'manisha_s@trimosmetrology.net']
       
      sendmail([self.doc.senders_email], self.doc.allocated_to, subject = 'Ticket Closed: %s, %s' % (self.doc.name, self.doc.subject) or '', parts = [['text/html',self.get_close_ticket_summary() or '']], cc = email_cc)
       
 
#posting response in table
  def post_response(self,arg):
    arg = eval(arg)
    res = Document('Ticket Response Detail')
    res.response =  arg['response']
    res.response_by = arg['response_by']
    res.response_date = nowdate();
    res.parent = arg['parent']
    res.parenttype = 'Ticket'
    res.parentfield = 'ticket_response_details'
    res.save(1)
    
    if self.doc.senders_email and self.doc.allocated_to:
      email = []
      email.append(self.doc.senders_email)
      email.append(self.doc.allocated_to)
      
      sendmail(email,'crm@trimosmetrology.net',subject = 'Response to Ticket:%s, %s' % (self.doc.name,self.doc.subject) or '',parts = [['text/html',self.get_response_summary(arg['response_by'],arg['response']) or '']])
        
    if not self.doc.allocated_to:
      msgprint('Please enter valid assignee_email')
      raise Exception

  def get_assignee_name(self):
    as_em = sql("select CONCAT(first_name,' ',ifnull(last_name,'')) from `tabProfile` where name=%s",self.doc.allocated_to)
    ret = { 'assignee_name' : as_em and as_em[0][0] or ''}
    return str(ret)
