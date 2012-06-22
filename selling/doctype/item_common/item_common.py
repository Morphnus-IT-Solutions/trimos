# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, getdate, has_common, month_name, now, nowdate, replace_newlines, sendmail, set_default, str_esc_quote, user_format, validate_email_add
from webnotes.model import db_exists
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname, SuperDocType
from webnotes.model.doclist import getlist, copy_doclist
from webnotes.model.code import get_obj, get_server_obj, run_server_obj, updatedb, check_syntax
from webnotes import session, form, is_testing, msgprint, errprint

sql = webnotes.conn.sql
get_value = webnotes.conn.get_value
in_transaction = webnotes.conn.in_transaction
convert_to_lists = webnotes.conn.convert_to_lists
	
# -----------------------------------------------------------------------------------------

class DocType:
	def __init__(self,d,dl):
		self.doc, self.doclist = d,dl

	# ------------------
	# Validate Defaults
	# ------------------
	def validate_defaults(self, obj, item_code = None):
		error = False
		if item_code and not sql("select name from tabItem where name = '%s' and docstatus != 2" % item_code):
			msgprint("Please select appropriate Item")
			error = True
		if not obj.doc.currency:
			msgprint("Please select Currency to get appropriate Ref Rate")
			error = True
		if not obj.doc.factor_figure_rate or obj.doc.factor_figure_rate == 0:
			msgprint("Please enter appropriate Factor Figure to calculate Ref Rate FCNR and Amount FCNR")
			error = True
		if not obj.doc.price_list:
			msgprint("Please select Price List to get appropriate Ref Rate")
			error = True
		return error

	# Get Item Details
	# ===============================================================
	def get_item_details(self, args, obj):
		args = eval(args)
		item, qty = args['item'], args['qty']
		ret = {}
		error = self.validate_defaults(obj, item)
		if not error:
			ref_rate = self.get_ref_rate(item, obj.doc.price_list, obj.doc.currency)
			ret['ref_rate_fcnr'] = flt(ref_rate)
			ret['ref_rate_inr'] = flt(ref_rate) * flt(obj.doc.factor_figure_rate)
			ret['amount_fcnr'] = flt(ref_rate) * flt(qty)
			ret['amount_inr'] = flt(ref_rate) * flt(qty) * flt(obj.doc.factor_figure_rate)
		return ret
	
	# ***************** Get Ref rate as entered in Item Master ********************
	def get_ref_rate(self, item_code, price_list_name, currency):
		ref_rate = sql("select ref_rate from `tabRef Rate Detail` where parent = %s and price_list_name = %s and ref_currency = %s", (item_code, price_list_name, currency))
		return ref_rate and ref_rate[0][0] or 0


	# -----------------
	# Calculate Amount
	# -----------------
	def calculate_amount(self, obj):
		for d in getlist(obj.doclist, obj.fname):
			error = self.validate_defaults(obj, d.item_code)
			if not error:
				ref_rate = self.get_ref_rate(d.item_code, obj.doc.price_list, obj.doc.currency)
			d.ref_rate_fcnr = flt(ref_rate)
			d.ref_rate_inr = flt(ref_rate) * flt(obj.doc.factor_figure_rate)
			d.amount_fcnr = flt(ref_rate) * flt(d.qty)
			d.amount_inr = flt(ref_rate) * flt(d.qty) * flt(obj.doc.factor_figure_rate)
	
