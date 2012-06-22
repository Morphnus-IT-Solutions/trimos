import webnotes
from webnotes.utils import load_json, cint, cstr, flt, get_defaults, nowdate
from webnotes.model.doc import Document, addchild, removechild, getchildren
from webnotes.model.doclist import getlist, copy_doclist
from webnotes import msgprint

sql = webnotes.conn.sql

class TransactionBase:

	# Get Customer Default Primary Address - first load
	# -----------------------
	def get_default_customer_address(self, args=''):
		address_text, address_name = self.get_address_text(customer=self.doc.customer)
		contact_text, contact_name, contact_email, contact_mobile, contact_department, contact_designation = self.get_contact_text(customer=self.doc.customer)
		self.doc.customer_address = address_name or ''
		self.doc.contact_person = contact_name or ''
		self.doc.address_display = address_text or ''
		self.doc.contact_display = contact_text or ''
		self.doc.contact_email = contact_email or ''
		self.doc.contact_mobile = contact_mobile or ''
		self.doc.contact_department = contact_department or ''
		self.doc.contact_designation = contact_designation or ''
		self.get_customer_details(self.doc.customer)
		self.get_sales_person(self.doc.customer)				
		
	# Get Customer Default Shipping Address - first load
	# -----------------------
	def get_default_customer_shipping_address(self, args=''):		
		address_text, address_name = self.get_address_text(customer=self.doc.customer,is_shipping_address=1)
		contact_text, contact_name, contact_email, contact_mobile, contact_department, contact_designation = self.get_contact_text(customer=self.doc.customer)		
		self.doc.customer_address = address_name or ''
		self.doc.contact_person = contact_name or ''
		self.doc.address_display = address_text or ''
		self.doc.contact_display = contact_text or ''
		self.doc.contact_email = contact_email or ''
		self.doc.contact_mobile = contact_mobile or ''
		self.doc.contact_department = contact_department or ''
		self.doc.contact_designation = contact_designation or ''
		
		self.get_customer_details(self.doc.customer)
		if self.doc.doctype != 'Quotation':
			self.get_sales_person(self.doc.customer)						

	# Get Customer Address
	# -----------------------
	def get_customer_address(self, args):
		args = load_json(args)		
		address_text, address_name = self.get_address_text(address_name=args['address'])
		contact_text, contact_name, contact_email, contact_mobile, contact_department, contact_designation = self.get_contact_text(contact_name=args['contact'])
		ret = {
			'customer_address' : address_name,
			'contact_person' : contact_name,
			'address_display' : address_text,
			'contact_display' : contact_text,
			'contact_email' : contact_email,
			'contact_mobile' : contact_mobile,
			'contact_department' : contact_department,
			'contact_designation' : contact_designation
		}
		return ret	
			
	# Get Address Text
	# -----------------------
	def get_address_text(self, customer=None, address_name=None, supplier=None, is_shipping_address=None):
		if customer:
			cond = customer and 'customer="%s"' % customer or 'name="%s"' % address_name
		elif supplier:
			cond = supplier and 'supplier="%s"' % supplier or 'name="%s"' % address_name	
		else:
			cond = 'name="%s"' % address_name	

		if is_shipping_address:
			details = sql("select name, address_line1, address_line2, city, country, pincode, state, phone from `tabAddress` where %s and docstatus != 2 order by is_shipping_address desc limit 1" % cond, as_dict = 1)
		else:
			details = sql("select name, address_line1, address_line2, city, country, pincode, state, phone from `tabAddress` where %s and docstatus != 2 order by is_primary_address desc limit 1" % cond, as_dict = 1)
		
		extract = lambda x: details and details[0] and details[0].get(x,'') or ''
		address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','phone')]
		address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
		if address_display.startswith('\n'): address_display = address_display[1:]		

		address_name = details and details[0]['name'] or ''
		return address_display, address_name

	# Get Contact Text
	# -----------------------
	def get_contact_text(self, customer=None, contact_name=None, supplier=None):
		if customer:
			cond = customer and 'customer="%s"' % customer or 'name="%s"' % contact_name
		elif supplier:
			cond = supplier and 'supplier="%s"' % supplier or 'name="%s"' % contact_name
		else:
			cond = 'name="%s"' % contact_name			
			
		details = sql("select name, first_name, last_name, email_id, phone, mobile_no, department, designation from `tabContact` where %s and docstatus != 2 order by is_primary_contact desc limit 1" % cond, as_dict = 1)

		extract = lambda x: details and details[0] and details[0].get(x,'') or ''
		contact_fields = [('','first_name'),('\n','lastname')]
		contact_display = ''.join([a[0]+extract(a[1]) for a in contact_fields if extract(a[1])])
		if contact_display.startswith('\n'): contact_display = contact_display[1:]
		
		contact_name = details and details[0]['name'] or ''
		contact_email = details and details[0]['email_id'] or ''
		contact_mobile = details and details[0]['mobile_no'] or ''
		contact_department = details and details[0]['department'] or ''
		contact_designation = details and details[0]['designation'] or ''
		return contact_display, contact_name, contact_email, contact_mobile, contact_department, contact_designation

	# Get Customer Details
	# -----------------------
	def get_customer_details(self, name):		
		customer_details = sql("select customer_name, customer_group, territory, zone, default_sales_partner, default_commission_rate from tabCustomer where name = '%s' and docstatus != 2" %(name), as_dict = 1)
		if customer_details:
			self.doc.customer_name = customer_details[0]['customer_name'] or ''
			self.doc.customer_group = customer_details[0]['customer_group'] or ''
			self.doc.territory = customer_details[0]['territory'] or ''
			self.doc.zone = customer_details[0]['zone'] or ''
			self.doc.sales_partner = customer_details[0]['default_sales_partner'] or ''
			self.doc.commission_rate = customer_details[0]['default_commission_rate'] or ''
			
	# Get Customer Shipping Address
	# -----------------------
	def get_shipping_address(self, name):
		details = sql("select name, address_line1, address_line2, city, country, pincode, state, phone from `tabAddress` where customer = '%s' and docstatus != 2 order by is_shipping_address desc limit 1" %(name), as_dict = 1)
		
		extract = lambda x: details and details[0] and details[0].get(x,'') or ''
		address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','phone')]
		address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
		if address_display.startswith('\n'): address_display = address_display[1:]
		
		ret = {
			'shipping_address_name' : details and details[0]['name'] or '',
			'shipping_address' : address_display
		}
		return ret
		
	# Get Lead Details
	# -----------------------
	def get_lead_details(self, name):		
		details = sql("select name, lead_name, address_line1, address_line2, city, country, state, pincode, territory, contact_no, mobile_no, email_id from `tabLead` where name = '%s'" %(name), as_dict = 1)		
		
		extract = lambda x: details and details[0] and details[0].get(x,'') or ''
		address_fields = [('','address_line1'),('\n','address_line2'),('\n','city'),(' ','pincode'),('\n','state'),('\n','country'),('\nPhone: ','contact_no')]
		address_display = ''.join([a[0]+extract(a[1]) for a in address_fields if extract(a[1])])
		if address_display.startswith('\n'): address_display = address_display[1:]
		
		ret = {
			'lead_name' : extract('lead_name'),
			'address_display' : address_display,
			'territory' : extract('territory'),
			'contact_mobile' : extract('mobile_no'),
			'contact_email' : extract('email_id')
		}
		return ret
		
		
	# Get Supplier Default Primary Address - first load
	# -----------------------
	def get_default_supplier_address(self, args):
		args = load_json(args)
		address_text, address_name = self.get_address_text(supplier=args['supplier'])
		contact_text, contact_name, contact_email, contact_mobile, contact_department, contact_designation = self.get_contact_text(supplier=args['supplier'])
		ret = {
			'supplier_address' : address_name,
			'address_display' : address_text,
			'contact_person' : contact_name,
			'contact_display' : contact_text,
			'contact_email' : contact_email,
			'contact_mobile' : contact_mobile,
			'contact_department' : contact_department,
			'contact_designation' : contact_designation
		}
		ret.update(self.get_supplier_details(args['supplier']))
		return ret
		
	# Get Supplier Address
	# -----------------------
	def get_supplier_address(self, args):
		args = load_json(args)
		address_text, address_name = self.get_address_text(address_name=args['address'])
		contact_text, contact_name, contact_email, contact_mobile = self.get_contact_text(contact_name=args['contact'])
		ret = {
			'supplier_address' : address_name,
			'address_display' : address_text,			
			'contact_person' : contact_name,
			'contact_display' : contact_text,
			'contact_email' : contact_email,
			'contact_mobile' : contact_mobile
		}
		return ret
	
	# Get Supplier Details
	# -----------------------
	def get_supplier_details(self, name):		
		supplier_details = sql("select supplier_name from tabSupplier where name = '%s' and docstatus != 2" %(name), as_dict = 1)
		ret = {
			'supplier_name' : supplier_details and supplier_details[0]['supplier_name'] or ''
		}
		return ret
		
	# Get Sales Person Details of Customer
	# ------------------------------------
	def get_sales_person(self, name):			
		self.doc.clear_table(self.doclist,'sales_team')
		idx = 0
		for d in sql("select sales_person, allocated_percentage, allocated_amount, incentives from `tabSales Team` where parent = '%s'" % name):
			ch = addchild(self.doc, 'sales_team', 'Sales Team', 1, self.doclist)
			ch.sales_person = d and cstr(d[0]) or ''
			ch.allocated_percentage = d and flt(d[1]) or 0
			ch.allocated_amount = d and flt(d[2]) or 0
			ch.incentives = d and flt(d[3]) or 0
			ch.idx = idx
			idx += 1
			
	# Get Company Specific Default Currency
	# -------------------------------------
	def get_company_currency(self, name):
		ret = sql("select default_currency from tabCompany where name = '%s'" %(name))
		dcc = ret and ret[0][0] or get_defaults()['currency']						
		return dcc


	# Set Serial No Warranty AMC History
	# ----------------------------------
	def update_serial_no_warranty_amc_status(self, serial_no_list = []):
		if serial_no_list:
			sr_list = serial_no_list
		else:
			sr_list = [s[0] for s in sql("select name from `tabSerial No` where docstatus = 1")]
		
		for s in sr_list:
			sr = Document('Serial No', s)
			if sr.amc_expiry_date:
				sr.warranty_amc_status = (sr.amc_expiry_date < nowdate()) and 'Out of AMC' or 'Under AMC'
			elif sr.warranty_expiry_date:
				sr.warranty_amc_status = (sr.warranty_expiry_date < nowdate()) and 'Out of Warranty' or 'Under Warranty'
			sr.save()
