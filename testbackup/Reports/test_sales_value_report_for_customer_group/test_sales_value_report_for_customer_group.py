# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import getdate
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Company/Warehouse"), "fieldname": "company_warehouse", "fieldtype": "Data", "width": 300},
    ]
    
    # Fetch all customer groups dynamically
    customer_groups = frappe.get_all("Customer Group", fields=["name"])
    customer_groups = customer_groups[:-1]
    for customer_group in customer_groups:
        columns.append({
            "label": _(customer_group.name),
            "fieldname": f"customer_group_{customer_group.name.lower().replace(' ', '_')}",
            "fieldtype": "Currency",
            "width": 180
        })

    columns.append({
        "label": _("Total"),
        "fieldname": "total_amount",
        "fieldtype": "Currency",
        "width": 180
    })
    
    return columns


def get_data(filters):
    # Company Filter
    company_filter = filters.get("company") if filters and filters.get("company") else None

    companies = frappe.get_all("Company", fields=["name"], filters={"name": company_filter} if company_filter else None)
    # Date Filters
    from_date_filter = filters.get("from_date") if filters and filters.get("from_date") else None
    to_date_filter = filters.get("to_date") if filters and filters.get("to_date") else None
    # Item Group Filter
    item_group_filter = filters.get("item_group") if filters and filters.get("item_group") else None
    data = []
    
    # Fetch data in all customer groups dynamically
    customer_groups = frappe.get_all("Customer Group", fields=["name"])
    
    for company in companies:
        company_row = {
            "company_warehouse": f"{company.name}",
            "indent": 0,
        }
        data.append(company_row)

        warehouses = frappe.get_all("Warehouse", filters={"company": company.name}, fields=["name"])
        warehouse_totals = {f"customer_group_{customer_group.name.lower().replace(' ', '_')}": 0.0 for customer_group in customer_groups}
        all_warehouses_row = None

        for warehouse in warehouses:
            row = {
                "company_warehouse": f"{warehouse.name}",
                "indent": 1
            }

            total_amount = 0.0

            for customer_group in customer_groups:    
                query = """
                    SELECT SUM(si.grand_total)
                    FROM `tabSales Invoice Item` sii
                    JOIN `tabSales Invoice` si ON sii.parent = si.name
                    JOIN `tabCustomer` c ON c.customer_name = si.customer_name
                    WHERE c.customer_group = %s
                    AND sii.warehouse = %s
                """

                params = [customer_group.name, warehouse.name]
                if from_date_filter:
                    query += " AND si.posting_date >= %s"
                    params.append(getdate(from_date_filter))

                if to_date_filter:
                    query += " AND si.posting_date <= %s"
                    params.append(getdate(to_date_filter))

                if item_group_filter:
                    query += " AND sii.item_group = %s"
                    params.append(item_group_filter)
                
                total = frappe.db.sql(query, tuple(params), as_dict=0)[0][0] or 0.0
                
                row[f"customer_group_{customer_group.name.lower().replace(' ', '_')}"] = total

                total_amount += total

                #  totals for all warehouses
                warehouse_totals[f"customer_group_{customer_group.name.lower().replace(' ', '_')}"] += total
            
            row["total_amount"] = total_amount

            # Check if this is the "All Warehouses" row
            if warehouse.name.startswith("All Warehouses - "):
                all_warehouses_row = row
            else:
                data.append(row)

        # After processing all warehouses, update the "All Warehouses" row if found
        if all_warehouses_row:
            all_warehouses_row["total_amount"] = sum(warehouse_totals.values())
            for customer_group in customer_groups:
                customer_group_key = f"customer_group_{customer_group.name.lower().replace(' ', '_')}"
                all_warehouses_row[customer_group_key] = warehouse_totals[customer_group_key]
            
            data.append(all_warehouses_row)

    return data
