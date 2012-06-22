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

from utilities.transaction_base import TransactionBase
# -----------------------------------------------------------------------------------------

class DocType(TransactionBase):
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist
    
  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.###')

  def send_mail(self):
    send_to = [self.doc.allocated_to, self.doc.contact_email]
    msg = '''%s Complaint Note raised by %s.
          Refer Complaint Note : %s
          '''%(self.doc.call_type, self.doc.complaint_raised_by, self.doc.name)
    sendmail(send_to, sender = 'automail@webnotestech.com', subject = 'Complaint Note', parts=[['text/plain', msg]])

  def on_submit(self):
    self.send_mail()
