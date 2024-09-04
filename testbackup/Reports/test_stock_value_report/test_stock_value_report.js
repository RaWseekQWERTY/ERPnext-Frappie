// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
//test
frappe.query_reports["Test Stock Value Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 0
		},
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date"
			
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default" : frappe.datetime.get_today(),
			"reqd" : 1
		}
	]
};