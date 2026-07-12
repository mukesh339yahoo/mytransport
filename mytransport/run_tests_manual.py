import frappe
import unittest
from mytransport.mytransport.doctype.lorry_receipt.test_lorry_receipt import IntegrationTestLorryReceipt

def run_tests_manual():
    frappe.flags.in_test = True
    suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestLorryReceipt)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()
