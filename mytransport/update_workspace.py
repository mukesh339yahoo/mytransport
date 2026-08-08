import frappe
import json
import os

def run():
    workspace_path = "/workspace/development/frappe-bench/apps/mytransport/mytransport/mytransport/workspace/transport/transport.json"
    with open(workspace_path, "r") as f:
        ws_data = json.load(f)

    ws = frappe.get_doc("Workspace", "Transport")
    ws.shortcuts = []
    ws.update(ws_data)
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("Workspace forced to sync with JSON!")
