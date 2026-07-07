import frappe

def run():
    lr_names = []
    for i in range(1, 11):
        lr_names.append({"name": f"TEST-LR-COMP-{i}", "amount": 1000})

    invoice_allocations = [
        (1, lr_names[0:3]), # 3 LRs
        (2, lr_names[3:7]), # 4 LRs
        (3, lr_names[7:10]) # 3 LRs
    ]
    
    invoices = []
    for inv_idx, lrs in invoice_allocations:
        total_amt = 0
        for lr_data in lrs:
            total_amt += lr_data["amount"]
        invoices.append({"name": f"TEST-INV-COMP-{inv_idx}", "amount": total_amt})

    print(invoices)

if __name__ == "__main__":
    run()
