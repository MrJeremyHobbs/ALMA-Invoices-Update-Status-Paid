#!/usr/bin/python3
import csv
import requests
import xmltodict

# configs
apikey = 'YOUR_API_KEY'

# get list of invoices with status "waiting to be paid"
r = requests.get(f"https://api-na.hosted.exlibrisgroup.com/almaws/v1/acq/invoices?invoice_workflow_status=Ready to be Paid&view=brief&limit=100&apikey={apikey}")
invoices_xml = r.text
invoices = xmltodict.parse(invoices_xml, dict_constructor=dict)

# parse invoice list
for invoice in invoices['invoices']['invoice']:
    invoice_number = invoice['number']
    invoice_alma_id = invoice['id']

    # search for a match in PeopleSoft transaction file
    with open('Transactions.csv', newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        
        # skip header
        next(reader)
        
        # parse rows
        for row in reader:
            document_id = row[6]
            invoice_id = row[8]
            date_posted = row[9]
            actuals = row[13]
            
            # update invoice to status "Paid" if found
            payload = f"""
<invoice>
 <payment>
   <voucher_date>{date_posted}</voucher_date>
   <voucher_amount>{actuals}</voucher_amount>
   <voucher_currency desc="US Dollar">USD</voucher_currency>
   <voucher_number>{document_id}</voucher_number>
 </payment>
</invoice>
"""
            if invoice_id == invoice_number:
                # post paid invoice
                url = f"https://api-na.hosted.exlibrisgroup.com/almaws/v1/acq/invoices/{invoice_alma_id}?op=paid&apikey={apikey}"
                headers = {'Content-Type': 'application/xml', 'charset':'UTF-8'}
                r = requests.post(url, data=payload.encode('utf-8'), headers=headers)