// // Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt


frappe.query_reports["Past 32 days Sales Transaction History"] = {
    "filters": [
        {
        "fieldname": "company",
        "label": "Company",
        "fieldtype": "Link",
        "options": "Company",
        "reqd": 0
    },
    {
        "fieldname": "item_group",
        "label":__("Item Group"),
        "fieldtype":"Link",
        "options":"Item"
    },
    {
        "fieldname": "customer_group",
        "label":__("Customer Group"),
        "fieldtype":"Link",
        "options":"Customer Group"
    }
]
};

