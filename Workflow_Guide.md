# Standard Operating Procedure: Transport Workflow

Welcome to your new Transport Management System! This document outlines the standard step-by-step workflow for a complete lifecycle—from booking cargo to collecting the final payment.

---

## Step 1: Book the Cargo (Lorry Receipt)
The journey begins when a customer asks you to transport goods.

1. Go to your **Transport Workspace** and click **Lorry Receipt**.
2. Click **Add Lorry Receipt**.
3. Select the **Branch**, **Date**, **Consignor**, and **Consignee**.
4. Select the **From City** and **To City** from the standard Territory list.
5. Enter the **Total Amount** (the freight charges the customer agrees to pay).
6. **Save** and **Submit**. 
7. *Result:* The LR is now active in the system, marked as `Unbilled` and `Unpaid`, waiting for a truck.

---

## Step 2: Dispatch the Truck (Challan)
When you are ready to load the goods into a truck (either your own or from a Broker), you create a Challan.

1. Go to your **Transport Workspace** and click **Challan**.
2. Click **Add Challan**.
3. Select the routing (**From Location** and **To Location**).
4. Under *Vehicle Details*, select the **Broker** (Supplier), **Vehicle Number**, and **Driver Name**.
5. In the **Lorry Receipts** table, add rows and select the specific Lorry Receipts you are loading onto this truck. *(You can add multiple LRs for a part-load trip).*
6. Under *Finance Details*, enter the **Total Hire Amount** (what you owe the Broker/Truck for this trip).
7. **Save** and **Submit**.

---

## Step 3: Pay Advances & Expenses (Expense Voucher)
When the truck departs, you often need to pay a Diesel Advance or Driver Bhatta.

1. Go to your **Transport Workspace** and click **Expense Voucher**.
2. Click **Add Expense Voucher**.
3. Select the **Expense Category** (e.g., *Trip Advance*).
4. Select the **Payment Type** (*Cash* or *Bank*) and the specific **Payment Account**.
5. Select the **Challan** number. *(The system will automatically pull in the Driver/Broker's name!)*
6. Enter the **Amount**.
7. **Save** and **Submit**.
8. *Behind the scenes:* ERPNext instantly creates a perfect double-entry **Journal Entry**, crediting your Bank/Cash account and debiting your Advance/Expense account.

---

## Step 4: Bill the Customer (Sales Invoice)
Once the goods are delivered (or according to your billing cycle), you must generate a bill to legally recognize the revenue and hit Accounts Receivable.

1. Go to your **Transport Workspace** and click **Sales Invoice** (or go to Accounting -> Sales Invoice).
2. Click **Add Sales Invoice** and select the **Customer**.
3. At the top of the form, click the custom **"Unbilled Lorry Receipts"** button!
4. A popup will appear showing all LRs for this customer that haven't been billed yet. Check the boxes next to the ones you want to bill, and click **Fetch LRs**.
5. A prompt will ask you to select an **Item Code** (e.g., your standard generic *Freight Charges* item).
6. The LRs magically populate as line items on your invoice with the correct amounts!
7. **Save** and **Submit**.
8. *Behind the scenes:* The selected LRs are permanently updated to `Billed` status so they can never be billed twice.

---

## Step 5: Collect Payment (Money Receipt)
When the customer finally sends a check or bank transfer, you need to record the receipt and clear the outstanding balances.

1. Go to your **Transport Workspace** and click **Money Receipt**.
2. Click **Add Money Receipt**.
3. Select the **Customer**, the **Payment Date**, and the **Payment Account** (where the money landed).
4. Enter the total **Paid Amount** received.
5. Click the custom **"Get Billed LRs"** button.
6. The system will fetch all of this customer's unpaid LRs. It automatically allocates the payment from oldest to newest.
   - *Tip:* If the customer short-paid a specific LR, you can manually override the amounts in the `Allocated Amount` column.
   - *Tip:* If they overpaid, the system tracks it automatically in the `Unallocated Amount` field for future credit!
7. **Save** and **Submit**.
8. *Behind the scenes:* ERPNext automatically generates a standard **Payment Entry**, perfectly reconciling the cash against the exact Sales Invoices. The LRs are instantly updated to show their new `Paid Amount` and `Outstanding Amount`!

---

### End of Workflow
You can monitor the health of your entire pipeline using the three custom reports:
- Use the **LR Register** to see all operations.
- Use the **LR Status Report** to see who owes you money.
- Use the **Challan Costing Report** to see how much profit you made on the trip!
