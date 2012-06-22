cur_frm.fields_dict['doc_doctype'].get_query = function(doc) {
 return 'select `tabDocType`.name from `tabDocType` where `tabDocType`.module not in ("Core", "System") and `tabDocType`.issingle != 1 and `tabDocType`.istable != 1  and `tabDocType`.name LIKE "%s" ORDER BY `tabDocType`.name LIMIT 50';
}
