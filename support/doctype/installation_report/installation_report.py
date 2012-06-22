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

class DocType:
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist

  def autoname(self):
    self.doc.name = make_autoname(self.doc.naming_series+'/.###')


  def get_service_person_details(self,name):
    det = sql("select mobile_no, designation, department, territory from `tabSales Person` where name = %s",(name),as_dict = 1)
    ret = {
      'contact_no'    :    det and det[0]['mobile_no'] or '',
      'designation'   :    det and det[0]['designation'] or '',
      'department'    :    det and det[0]['department'] or '',
      'territory'     :    det and det[0]['territory'] or ''
    }
    return str(ret)

  # ---------------------
  # get customer details
  # ---------------------
  def get_customer_details(self):
    self.get_default_customer_address()
    self.get_default_contact_details()


