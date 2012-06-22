import webnotes
from webnotes import msgprint

feed_dict = {
	# Project
	'Project':		       ['[%(status)s]', '#000080'],

	# Sales
	'Lead':			 ['%(lead_name)s', '#FFBF00'],
	'Quotation':	    ['[%(status)s] To %(customer_name)s worth %(currency)s %(grand_total_export)s', '#4169E1'],
	'Sales Order':	  ['[%(status)s] To %(customer_name)s worth %(currency)s %(grand_total_export)s', '#04B404'],

	# Purchase
	'Supplier':		     ['%(supplier_name)s, %(supplier_type)s', '#6495ED'],
	'Purchase Order':       ['[%(status)s] %(name)s To %(supplier_name)s for %(currency)s  %(grand_total_import)s', '#4169E1'],

	# Stock
	'Delivery Note':	['[%(status)s] To %(customer_name)s', '#DF3A01'],

	# Accounts
	'Journal Voucher':      ['[%(voucher_type)s] %(name)s', '#4169E1'],
	'Payable Voucher':      ['To %(supplier_name)s for %(currency)s %(grand_total_import)s', '#4169E1'],
	'Receivable Voucher':['To %(customer_name)s for %(currency)s %(grand_total_export)s', '#4169E1'],

	# HR
	'Expense Voucher':      ['[%(approval_status)s] %(name)s by %(employee_name)s', '#4169E1'],
	'Salary Slip':	  ['%(employee_name)s for %(month)s %(fiscal_year)s', '#4169E1'],
	'Leave Transaction':['%(leave_type)s for %(employee)s', '#4169E1'],

	# Support
	'Customer Issue':       ['[%(status)s] %(description)s by %(customer_name)s', '#ED144A'],
	'Maintenance Visit':['To %(customer_name)s', '#4169E1'],
	'Support Ticket':       ['[%(status)s] %(subject)s', '#000080'],
    'Service Quotation': ['[%(status)s] %(quotation_type)s to %(customer_name)s worth %(currency)s %(grand_total_export)s', '#CB21E5'],
    'Service Order': ['[%(status)s] %(order_type)s to %(customer_name)s worth %(currency)s %(grand_total_export)s', '#01DFD7'],
    'Monthly Visit Schedule': ['[%(status)s] %(prepared_by)s for %(month)s', '#DF01D7'],
    'Visit Report': ['[%(status)s] %(prepared_by)s for %(month)s', '#AEB404'],
	'Service Report': ['[%(status)s] %(engineer_name_1)s. Type of Visit : %(type_of_visit)s', '#A4A4A4'],
	'Calibration Certificate': ['[%(status)s] %(calibrated_by)s for %(serial_no)s', '#1DE9B9'],
}

feed_dict_color = {
	# Project
	'Project': '#000080',
	
	# Sales
	'Lead':	'#FFBF00',
	'Quotation': '#4169E1',
	'Sales Order': '#04B404',

	# Purchase
	'Supplier': '#6495ED',
	'Purchase Order': '#4169E1',

	# Stock
	'Delivery Note': '#DF3A01',

	# Accounts
	'Journal Voucher': '#4169E1',
	'Payable Voucher': '#4169E1',
	'Receivable Voucher': '#4169E1',

	# HR
	'Expense Voucher': '#4169E1',
	'Salary Slip': '#4169E1',
	'Leave Transaction': '#4169E1',

	# Support
	'Customer Issue': '#ED144A',
	'Maintenance Visit': '#4169E1',
	'Support Ticket': '#000080'
}

def make_feed(doc, subject, color):
	"makes a new Feed record"
	#msgprint(subject)
	from webnotes.model.doc import Document
	webnotes.conn.sql("delete from tabFeed where doc_type=%s and doc_name=%s", (doc.doctype, doc.name))
	f = Document('Feed')
	f.doc_type = doc.doctype
	f.doc_name = doc.name
	f.subject = subject
	f.color = color
	f.save(1)

def update_feed1(doc):   
	"adds a new feed"
	prop_rec = webnotes.conn.sql("select value from `tabProperty Setter` where doc_type = %s and property = 'subject'", (doc.doctype))
	if prop_rec:		
		subject = prop_rec[0][0]
	else:	
		rec = webnotes.conn.sql("select subject from tabDocType where name=%s", (doc.doctype))
		subject = rec[0][0]
	
	subject, color = [subject, feed_dict_color.get(doc.doctype)]
	if subject:
		subject = subject % doc.fields
		make_feed(doc, subject, color)
		
def update_feed(doc, method=None):   
	"adds a new feed"
	if method=='validate':
		return
	subject, color = feed_dict.get(doc.doctype, [None, None])
	if subject:
		subject = subject % doc.fields
		make_feed(doc, subject, color)
