import frappe
from frappe.utils import add_days, nowdate, getdate
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Company/Warehouse"), "fieldname": "company_warehouse", "fieldtype": "Data", "width": 300},
    ]
    
    # Dynamically add columns for the last 32 days
    today = getdate(nowdate())
    for i in range(32):
        date = add_days(today, -i)
        columns.append({
            "label": date.strftime("%m/%d/%Y"),
            "fieldname": f"date_{i}",
            "fieldtype": "Currency",
            "width": 130
        })
    
    return columns

def get_data(filters):
    # Apply filters if provided
    company_filter = filters.get("company") if filters and filters.get("company") else None

    companies = frappe.get_all("Company", fields=["name"], filters={"name": company_filter} if company_filter else None)
    
    #Customer Group Filter
    customer_group_filter = filters.get("customer_group") if filters and filters.get("customer_group") else None
    
    # Item Group Filter
    item_group_filter = filters.get("item_group") if filters and filters.get("item_group") else None

    data = []
    today = getdate(nowdate())
    
    for company in companies:
        # Add company as a parent row with indent level 0 and no date fields
        company_row = {
            "company_warehouse": f"{company.name}",
            "indent": 0,
        }
        data.append(company_row)

        # Fetch all warehouses under this company
        warehouses = frappe.get_all("Warehouse", filters={"company": company.name}, fields=["name"])

        warehouse_totals = {}  # Store totals by warehouse
        all_warehouses_row = None  # Store the "All Warehouses" row

        for warehouse in warehouses:
            row = {
                "company_warehouse": f"{warehouse.name}",
                "indent": 1  # Child rows have an indent level of 1
            }

            for i in range(32):
                date = add_days(today, -i)
                date_str = date.strftime('%Y-%m-%d')

                # Query to sum up the grand_total for the warehouse on this date
                query = """
                    SELECT SUM(si.grand_total)
                    FROM `tabSales Invoice` si
                    JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
                    JOIN `tabCustomer` c ON c.customer_name = si.customer_name
                    WHERE sii.warehouse = %s
                    AND DATE(si.posting_date) = %s
                """

                params = [warehouse.name, date_str]
                if customer_group_filter:
                    query += "AND c.customer_group = %s"
                    params.append(customer_group_filter)
                if item_group_filter:
                    query += " AND sii.item_group = %s"
                    params.append(item_group_filter)
                    
                total = frappe.db.sql(query, tuple(params), as_dict=0)[0][0]

                row[f"date_{i}"] = total or 0.0

                # Store the total for summing later
                warehouse_totals[f"date_{i}"] = warehouse_totals.get(f"date_{i}", 0) + (total or 0.0)

            # Check if the warehouse is the "All Warehouses" for the company
            if warehouse.name.startswith("All Warehouses - "):
                all_warehouses_row = row
            else:
                data.append(row)

        # After processing all warehouses, add the "All Warehouses" row if found
        if all_warehouses_row:
            # Sum the totals from other warehouses under this company
            for i in range(32):
                all_warehouses_row[f"date_{i}"] = warehouse_totals[f"date_{i}"]
            data.append(all_warehouses_row)

    return data
