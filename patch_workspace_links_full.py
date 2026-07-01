import json
import os

ws_path = "apps/mytransport/mytransport/mytransport/workspace/transport/transport.json"

with open(ws_path, "r") as f:
    doc = json.load(f)

# Clear existing links
doc["links"] = []

# Create Documents section
doc["links"].append({
    "hidden": 0,
    "is_query_report": 0,
    "label": "Documents",
    "link_count": 0,
    "link_type": "DocType",
    "onboard": 0,
    "type": "Card Break"
})

docs = [
    ("Lorry Receipt", "DocType"),
    ("Challan", "DocType"),
    ("Transport Invoice", "DocType"),
    ("Money Receipt", "DocType"),
    ("Expense Voucher", "DocType")
]

for label, link_type in docs:
    doc["links"].append({
        "hidden": 0,
        "is_query_report": 0,
        "label": label,
        "link_count": 0,
        "link_to": label,
        "link_type": link_type,
        "onboard": 0,
        "type": "Link"
    })

# Create Reports section
doc["links"].append({
    "hidden": 0,
    "is_query_report": 0,
    "label": "Reports",
    "link_count": 0,
    "link_type": "DocType",
    "onboard": 0,
    "type": "Card Break"
})

reports = [
    ("LR Register", "Report"),
    ("LR Status Report", "Report"),
    ("Challan Costing Report", "Report"),
    ("Challan Register", "Report")
]

for label, link_type in reports:
    doc["links"].append({
        "hidden": 0,
        "is_query_report": 0,
        "label": label,
        "link_count": 0,
        "link_to": label,
        "link_type": link_type,
        "onboard": 0,
        "type": "Link"
    })

with open(ws_path, "w") as f:
    json.dump(doc, f, indent=1)

