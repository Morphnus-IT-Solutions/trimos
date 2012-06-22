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
		self.doc, self.doclist = d,dl
	
	# Create default accounts
	# ---------------------------------------------------
	def create_default_accounts(self):
		self.fld_dict = {'account_name':0,'parent_account':1,'group_or_ledger':2,'is_pl_account':3,'account_type':4,'debit_or_credit':5,'company':6,'tax_rate':7}
		acc_list_common = [['Application of Funds (Assets)','','Group','No','','Debit',self.doc.name,''],
												['Current Assets','Application of Funds (Assets)','Group','No','','Debit',self.doc.name,''],
													['Accounts Receivable','Current Assets','Group','No','','Debit',self.doc.name,''],
													['Bank Accounts','Current Assets','Group','No','Bank or Cash','Debit',self.doc.name,''],
													['Cash In Hand','Current Assets','Group','No','Bank or Cash','Debit',self.doc.name,''],
														['Cash','Cash In Hand','Ledger','No','Bank or Cash','Debit',self.doc.name,''],
													['Loans and Advances (Assets)','Current Assets','Group','No','','Debit',self.doc.name,''],
													['Securities and Deposits','Current Assets','Group','No','','Debit',self.doc.name,''],
														['Earnest Money','Securities and Deposits','Ledger','No','','Debit',self.doc.name,''],
													['Stock In Hand','Current Assets','Group','No','','Debit',self.doc.name,''],
														['Stock','Stock In Hand','Ledger','No','','Debit',self.doc.name,''],
													['Tax Assets','Current Assets','Group','No','','Debit',self.doc.name,''],
												['Fixed Assets','Application of Funds (Assets)','Group','No','','Debit',self.doc.name,''],
													['Capital Equipments','Fixed Assets','Ledger','No','Fixed Asset Account','Debit',self.doc.name,''],
													['Computers','Fixed Assets','Ledger','No','Fixed Asset Account','Debit',self.doc.name,''],
													['Furniture and Fixture','Fixed Assets','Ledger','No','Fixed Asset Account','Debit',self.doc.name,''],
													['Office Equipments','Fixed Assets','Ledger','No','Fixed Asset Account','Debit',self.doc.name,''],
													['Plant and Machinery','Fixed Assets','Ledger','No','Fixed Asset Account','Debit',self.doc.name,''],
												['Investments','Application of Funds (Assets)','Group','No','','Debit',self.doc.name,''],
												['Temporary Accounts (Assets)','Application of Funds (Assets)','Group','No','','Debit',self.doc.name,''],
													['Temporary Account (Assets)','Temporary Accounts (Assets)','Ledger','No','','Debit',self.doc.name,''],
									['Source of Funds (Liabilities)','','Group','No','','Credit',self.doc.name,''],
										['Capital Account','Source of Funds (Liabilities)','Group','No','','Credit',self.doc.name,''],
											['Reserves and Surplus','Capital Account','Group','No','','Credit',self.doc.name,''],
											['Shareholders Funds','Capital Account','Group','No','','Credit',self.doc.name,''],
										['Current Liabilities','Source of Funds (Liabilities)','Group','No','','Credit',self.doc.name,''],
											['Accounts Payable','Current Liabilities','Group','No','','Credit',self.doc.name,''],
											['Duties and Taxes','Current Liabilities','Group','No','','Credit',self.doc.name,''],
											['Loans (Liabilities)','Current Liabilities','Group','No','','Credit',self.doc.name,''],
												['Secured Loans','Loans (Liabilities)','Group','No','','Credit',self.doc.name,''],
												['Unsecured Loans','Loans (Liabilities)','Group','No','','Credit',self.doc.name,''],
												['Bank Overdraft Account','Loans (Liabilities)','Group','No','','Credit',self.doc.name,''],
										['Temporary Accounts (Liabilities)','Source of Funds (Liabilities)','Group','No','','Credit',self.doc.name,''],
											['Temporary Account (Liabilities)','Temporary Accounts (Liabilities)','Ledger','No','','Credit',self.doc.name,''],
									['Income','','Group','Yes','','Credit',self.doc.name,''],
										['Direct Income','Income','Group','Yes','Income Account','Credit',self.doc.name,''],
											['Sales','Direct Income','Ledger','Yes','Income Account','Credit',self.doc.name,''],
											['Service','Direct Income','Ledger','Yes','Income Account','Credit',self.doc.name,''],
										['Indirect Income','Income','Group','Yes','Income Account','Credit',self.doc.name,''],
									['Expenses','','Group','Yes','Expense Account','Debit',self.doc.name,''],
										['Direct Expenses','Expenses','Group','Yes','Expense Account','Debit',self.doc.name,''],
											['Cost of Goods Sold','Direct Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
										['Indirect Expenses','Expenses','Group','Yes','Expense Account','Debit',self.doc.name,''],
											['Advertising and Publicity','Indirect Expenses','Ledger','Yes','Chargeable','Debit',self.doc.name,''],
											['Bad Debts Written Off','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Bank Charges','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Books and Periodicals','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Charity and Donations','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Commission on Sales','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Conveyance Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Customer Entertainment Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Depreciation Account','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Freight and Forwarding Charges','Indirect Expenses','Ledger','Yes','Chargeable','Debit',self.doc.name,''],
											['Legal Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Miscellaneous Expenses','Indirect Expenses','Ledger','Yes','Chargeable','Debit',self.doc.name,''],
											['Office Maintenance Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Office Rent','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Postal Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Print and Stationary','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Rounded Off','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Salary','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Sales Promotion Expenses','Indirect Expenses','Ledger','Yes','Chargeable','Debit',self.doc.name,''],
											['Service Charges Paid','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Staff Welfare Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Telephone Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Travelling Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,''],
											['Water and Electricity Expenses','Indirect Expenses','Ledger','Yes','Expense Account','Debit',self.doc.name,'']
									]
		
		acc_list_india = [
											['CENVAT Capital Goods','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['CENVAT','Tax Assets','Ledger','No','Chargeable','Debit',self.doc.name,''],
											['CENVAT Service Tax','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['CENVAT Service Tax Cess 1','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['CENVAT Service Tax Cess 2','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['CENVAT Edu Cess','Tax Assets','Ledger','No','Chargeable','Debit',self.doc.name,''],
											['CENVAT SHE Cess','Tax Assets','Ledger','No','Chargeable','Debit',self.doc.name,''],
											['Excise Duty 4','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'4.00'],
											['Excise Duty 8','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'8.00'],
											['Excise Duty 10','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'10.00'],
											['Excise Duty 14','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'14.00'],
											['Excise Duty Edu Cess 2','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'2.00'],
											['Excise Duty SHE Cess 1','Tax Assets','Ledger','No','Tax','Debit',self.doc.name,'1.00'],
											['P L A','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['P L A - Cess Portion','Tax Assets','Ledger','No','','Debit',self.doc.name,''],
											['Edu. Cess on Excise','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'2.00'],
											['Edu. Cess on Service Tax','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'2.00'],
											['Edu. Cess on TDS','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'2.00'],
											['Excise Duty @ 4','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'4.00'],
											['Excise Duty @ 8','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'8.00'],
											['Excise Duty @ 10','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'10.00'],
											['Excise Duty @ 14','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'14.00'],
											['Service Tax','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'10.3'],
											['SHE Cess on Excise','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'1.00'],
											['SHE Cess on Service Tax','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'1.00'],
											['SHE Cess on TDS','Duties and Taxes','Ledger','No','Tax','Credit',self.doc.name,'1.00'],
											['Professional Tax','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['VAT','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Advertisement)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Commission)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Contractor)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Interest)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Rent)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,''],
											['TDS (Salary)','Duties and Taxes','Ledger','No','','Credit',self.doc.name,'']
										 ]
		# load common account heads
		for d in acc_list_common:
			self.add_acc(d)

		country = sql("select value from tabSingles where field = 'country' and doctype = 'Control Panel'")
		country = country and cstr(country[0][0]) or ''

		# load taxes (only for India)
		if country == 'India':
			for d in acc_list_india:
				self.add_acc(d)

	# Create account
	# ---------------------------------------------------
	def add_acc(self,lst):
		ac = Document('Account')
		for d in self.fld_dict.keys():
			ac.fields[d] = (d == 'parent_account' and lst[self.fld_dict[d]]) and lst[self.fld_dict[d]] +' - '+ self.doc.abbr or lst[self.fld_dict[d]]
		ac.old_parent = ''
		ac_obj = get_obj(doc=ac)
		ac_obj.validate()
		ac_obj.doc.save(1)
		ac_obj.on_update()
		sql("commit")
		sql("start transaction")


	# Set letter head
	# ---------------------------------------------------
	def set_letter_head(self):
		if not self.doc.letter_head:
			if self.doc.address:
				header = """ 
<div><h3> %(comp)s </h3> %(add)s </div>

			""" % {'comp':self.doc.name,
				 'add':self.doc.address.replace("\n",'<br>')}
			 
				self.doc.letter_head = header

	# Set default AR and AP group
	# ---------------------------------------------------
	def set_default_groups(self):
		if not self.doc.receivables_group:
			set(self.doc, 'receivables_group', 'Application of Funds - '+self.doc.abbr)
		if not self.doc.payables_group:
			set(self.doc, 'payables_group', 'Source of Funds - '+self.doc.abbr)
			
			
	# Create default cost center
	# ---------------------------------------------------
	def create_default_cost_center(self):
		glc = get_obj('GL Control')
		cc_list = [{'cost_center_name':'Root','company_name':self.doc.name,'company_abbr':self.doc.abbr,'group_or_ledger':'Group','parent_cost_center':'','old_parent':''}, {'cost_center_name':'Default CC Ledger','company_name':self.doc.name,'company_abbr':self.doc.abbr,'group_or_ledger':'Ledger','parent_cost_center':'Root - ' + self.doc.abbr,'old_parent':''}]
		for c in cc_list:
			glc.add_cc(str(c))
			
			
	# On update
	# ---------------------------------------------------
	def on_update(self):
		self.set_letter_head()
		ac = sql("select name from tabAccount where account_name='Income' and company=%s", self.doc.name)
		if not ac:
			self.create_default_accounts()
		self.set_default_groups()
		cc = sql("select name from `tabCost Center` where cost_center_name = 'Root' and company_name = '%s'"%(self.doc.name))
		if not cc:
			self.create_default_cost_center()

	# Trash accounts and cost centers for this company
	# ---------------------------------------------------
	#def on_trash1(self):
	#	acc = sql("select name from tabAccount where company = '%s' and docstatus != 2 order by lft desc, rgt desc limit 2" % self.doc.name, debug=1)
	#	for each in acc:
	#		get_obj('Account', each[0]).on_trash()
			
	#	cc = sql("select name from `tabCost Center` where company_name = '%s' and docstatus != 2" % self.doc.name)
	#	for each in cc:
	#		get_obj('Cost Center', each[0]).on_trash()
		
	#	msgprint("Company trashed. All the accounts and cost centers related to this company also trashed. You can restore it anytime from Setup -> Manage Trash")
		
	def on_trash(self):
		rec = sql("SELECT sum(ab.opening), sum(ab.balance), sum(ab.debit), sum(ab.credit) FROM `tabAccount Balance` ab, `tabAccount` a WHERE ab.account = a.name and a.company = %s", self.doc.name)
		if rec[0][0] == 0 and rec[0][1] == 0 and rec[0][2] == 0 and rec[0][3] == 0:
			#delete tabAccount Balance
			sql("delete ab.* from `tabAccount Balance` ab, `tabAccount` a where ab.account = a.name and a.company = %s", self.doc.name)
			#delete tabAccount
			sql("delete from `tabAccount` where company = %s order by lft desc, rgt desc", self.doc.name)
			
			#delete cost center child table - budget detail
			sql("delete bd.* from `tabBudget Detail` bd, `tabCost Center` cc where bd.parent = cc.name and cc.company_name = %s", self.doc.name)
			#delete cost center
			sql("delete from `tabCost Center` WHERE company_name = %s order by lft desc, rgt desc", self.doc.name)
			
			#update value as blank for tabDefaultValue defkey=company
			sql("update `tabDefaultValue` set defvalue = '' where defkey='company' and defvalue = %s", self.doc.name)
			
			#update value as blank for tabSingles Manage Account
			sql("update `tabSingles` set value = '' where doctype='Manage Account' and field = 'default_company' and value = %s", self.doc.name)

	# Restore accounts and cost centers for this company
	# ---------------------------------------------------
	def on_restore(self):
		acc = sql("select name from tabAccount where company = '%s' and docstatus = 2" % self.doc.name)
		for each in acc:
			get_obj('Account', each[0]).on_restore()
			
		cc = sql("select name from `tabCost Center` where company_name = '%s' and docstatus = 2" % self.doc.name)
		for each in cc:
			get_obj('Cost Center', each[0]).on_restore()
		
		msgprint("Company restored. All the accounts and cost centers related to this company also restored.")
		
	# on rename
	# ---------
	def on_rename(self,newdn,olddn):		
		sql("update `tabCompany` set company_name = '%s' where name = '%s'" %(newdn,olddn))						
