# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import add_days, nowdate, getdate
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    # report_summary = get_report_summary(data)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Company/Warehouse"), "fieldname": "company_warehouse", "fieldtype": "Data", "width": 300},
    ]
    
    # Fetch all item groups dynamically, including "All Item Group"
    item_groups = frappe.get_all("Item Group", fields=["name"])
    item_groups = item_groups[:-1]
    
    for item_group in item_groups:
        columns.append({
            "label": _(item_group.name),
            "fieldname": f"item_group_{item_group.name.lower().replace(' ', '_')}",
            "fieldtype": "Currency",
            "width": 150
        })
    columns.append({
        "label": _("Total"),
        "fieldname": "all_item_group",
        "fieldtype": "Currency",
        "width": 150
    })
    
    return columns

def get_data(filters):
    # Company Filter
    company_filter = filters.get("company") if filters and filters.get("company") else None

    companies = frappe.get_all("Company", fields=["name"], filters={"name": company_filter} if company_filter else None)
    # Date Filters
    from_date_filter = filters.get("from_date") if filters and filters.get("from_date") else None
    to_date_filter = filters.get("to_date") if filters and filters.get("to_date") else None
	#Customer Group Filter
    customer_group_filter = filters.get("customer_group") if filters and filters.get("customer_group") else None
    data = []
    
    # Fetch all item groups dynamically
    item_groups = frappe.get_all("Item Group", fields=["name"])
    #Fetching all companies in row 
    for company in companies:
        company_row = {
            "company_warehouse": f"{company.name}",
            "indent": 0,
        }
        data.append(company_row)

        warehouses = frappe.get_all("Warehouse", filters={"company": company.name}, fields=["name"])
        #every warehouse total is 0 at first
        warehouse_totals = {f"item_group_{item_group.name.lower().replace(' ', '_')}": 0.0 for item_group in item_groups}
        all_warehouses_row = None
        # Inner Loop for fetching warehouses present inside a company
        for warehouse in warehouses:
            row = {
                "company_warehouse": f"{warehouse.name}",
                "indent": 1
           }

            all_item_group_total = 0.0
            #Query for each item_group
            for item_group in item_groups:    
                query = """
                    SELECT SUM(sii.actual_qty)
                    FROM `tabSales Invoice Item` sii
                    JOIN `tabSales Invoice` si ON sii.parent = si.name
                    JOIN `tabCustomer` c ON c.customer_name = si.customer_name
                    WHERE sii.item_group = %s
                    AND sii.warehouse = %s
                   
                """

                params = [item_group.name, warehouse.name]
                if from_date_filter:
                    query += " AND sii.creation >= %s"
                    params.append(getdate(from_date_filter))

                if to_date_filter:
                    query += " AND sii.creation <= %s"
                    params.append(getdate(to_date_filter))

                if customer_group_filter:
                    query += "AND c.customer_group = %s"
                    params.append(customer_group_filter) 
                
                total = frappe.db.sql(query, tuple(params), as_dict=0)[0][0] or 0.0
                
                row[f"item_group_{item_group.name.lower().replace(' ', '_')}"] = total

                all_item_group_total += total

                # Accumulate totals for all warehouses
                warehouse_totals[f"item_group_{item_group.name.lower().replace(' ', '_')}"] += total
            
            row["all_item_group"] = all_item_group_total

            # Check if this is the "All Warehouses" row
            if warehouse.name.startswith("All Warehouses - "):
                all_warehouses_row = row
            else:
                data.append(row)

        # After processing all warehouses, update the "All Warehouses" row if found
        if all_warehouses_row:
            # Initialize all_item_group_total for "All Warehouses" row
            all_warehouses_row["all_item_group"] = sum(warehouse_totals.values())
            for item_group in item_groups:
                item_group_key = f"item_group_{item_group.name.lower().replace(' ', '_')}"
                all_warehouses_row[item_group_key] = warehouse_totals[item_group_key]
            
            data.append(all_warehouses_row)

    return data

""" def get_report_summary(data):
    total_rs = 0.0
    total_warehouses = 0

    for row in data:
        if row["indent"] == 1: 
            total_rs += row.get("all_item_group", 0.0)
            total_warehouses += 1

    report_summary = [
        {"label": "Total Rs", "value": f"{total_rs:,.2f}", "indicator": "Green"},
        {"label": "Total Warehouses", "value": total_warehouses, "indicator": "Blue"}
    ]

    return report_summary
 """