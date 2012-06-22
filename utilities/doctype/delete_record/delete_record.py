import webnotes

from webnotes import msgprint
from webnotes.model import delete_doc
sql = webnotes.conn.sql

class DocType:
  def __init__(self, d, dl):
    self.doc, self.doclist = d, dl

  def delete_record(self):
    exists = sql("select name from `tab%s` where name = '%s'"%(self.doc.doc_doctype, self.doc.record_name))
    if not exists:
      msgprint("%s : %s does not exist."%(self.doc.doc_doctype, self.doc.record_name))
      raise Exception
    else:
      sql("update `tab%s` set docstatus = 2 where name = '%s'" % (self.doc.doc_doctype, self.doc.record_name))
      if self.doc.doc_doctype == 'Price List':
        sql("delete from `tabRef Rate Detail` where price_list_name = %s", self.doc.record_name)
      msgprint("Deleted %s : %s" % (self.doc.doc_doctype, self.doc.record_name))
