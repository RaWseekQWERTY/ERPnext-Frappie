// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Test Sales Value Report"] = {
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
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group",
		}
		// {
        //     "fieldname": "period",
        //     "label": "Period",
        //     "fieldtype": "Select",
        //     "options": "\nDaily\nWeekly\nMonthly",
        //     "default": "Daily",
        //     "reqd": 1,
        //     "on_change": function() {
        //         let period = frappe.query_report.get_filter_value('period');
        //         let today = frappe.datetime.get_today();
        //         let from_date;

        //         if (period === "Daily") {
        //             from_date = today;
        //         } else if (period === "Weekly") {
        //             from_date = frappe.datetime.add_days(today, -7);
        //         } else if (period === "Monthly") {
        //             from_date = frappe.datetime.add_months(today, -1);
        //         }

        //         frappe.query_report.set_filter_value('from_date', from_date);
        //         frappe.query_report.set_filter_value('to_date', today);
        //     }
        // }
	]
};
