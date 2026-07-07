import frappe
from mytransport.mytransport.doctype.lorry_receipt.test_lorry_receipt import IntegrationTestLorryReceipt
import traceback

def run():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    print("Running All Custom Tests...")
    tests = [
        'test_end_to_end_transport_lifecycle',
        'test_end_to_end_multiple_lrs',
        'test_end_to_end_complex_batching'
    ]
    
    for test_name in tests:
        try:
            print(f"\n--- Running {test_name} ---")
            test_instance = IntegrationTestLorryReceipt(methodName=test_name)
            test_instance.setUp()
            getattr(test_instance, test_name)()
            print(f"{test_name} Passed Successfully!")
        except Exception as e:
            print(f"{test_name} FAILED:")
            traceback.print_exc()
        finally:
            frappe.db.rollback()
            
if __name__ == "__main__":
    run()
