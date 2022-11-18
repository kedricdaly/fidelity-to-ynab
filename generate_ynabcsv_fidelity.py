import csv
import re
from datetime import datetime
from tkinter import Tk

class Transaction_fid:
    def __init__(self, date, source, transaction_type, amount):
        self.date = date # MM/DD/YYYY, as string
        self.source = source.title()
        self.transaction_type = transaction_type.title()
        self.amount = float(amount.replace('$','')) # remove '$' to allow for float datatype

    def __str__(self):
        return f'{self.date}, {self.source}, {self.transaction_type}. {self.amount}'

    def get_payees(self):
        '''
        Generate payee table. Keys are lowercase. Values are for YNAB
        '''
        return {
            '1 - employee deferral': '401(k)',
            '1 - employee deferrals': '401(k)',
            '2 - employer match': '401(k) match',
            '2 - safe harbor matching': '401(k) match',
            '4 - employer discretionary': '401(k) discretionary',
            '9 - roth basic': 'Roth 401(k)',
            '11 - roth deferral': 'Roth 401(k)',
            'balance forward': 'Balance Forward',
            'dividend': 'Dividend',
            'realized gain/loss': 'Realized gains/losses',
            'recordkeeping fee': 'Fees',
            'revenue credit': 'Revenue Credit',
            'administrative fees': 'Fees',
            'change in market value': 'Change in Market Value'
        }

    def normalize_payee(self, payees):
        try:
            if self.transaction_type.lower() == 'contributions':
                return payees[self.source.lower()]
            else:
                return payees[self.transaction_type.lower()]
        except:
            return 'Source or transaction type not in payees dictionary'

    def generate_ynab4_memo(self):
        try:
            dtime = datetime.strptime(self.date,'%m/%d/%Y')
            return ':'.join([dtime.strftime('%Y%m%d'), self.source, self.transaction_type])
        except:
            return f'Could not create memo for transaction: {self}'

class Transaction_YNAB4:
        def __init__(self, date, payee, category=None, memo=None, outflow=None, inflow=None):
            self.date = date # MM/DD/YYYY, as string
            self.payee = payee
            self.category = category
            self.memo = memo
            self.outflow = outflow
            self.inflow = inflow

        def __str__(self):
            return f'{self.date}, {self.payee}, {self.category}. {self.memo}, {self.outflow}, {self.inflow}'

        def __iter__(self):
            '''
            Used for writing to csv, and is therefore YNAB output
            YNAB CSV order: Date, Payee, Category, Memo, Outflow, Inflow
            '''
            return iter([self.date, self.payee, self.category, self.memo, self.outflow, self.inflow])

def generate_ynab4_header():
    return ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']

def remove_showdetails(raw):
    pattern = re.compile('\n\n.*\n\t', re.M)
    details = re.findall(pattern, raw)
    for item in details:
        raw = raw.replace(item,'\t')  
    return raw

def clean_raw_data(raw):
    no_details = remove_showdetails(raw)
    records = no_details.split('\n')
    splits = [record.split('\t') for record in records]
    return [[col.strip() for col in record] for record in splits]

def create_transactions_fid(records):
    # removes share info from Transaction_fids
    return [Transaction_fid(*record[:-1]) for record in records]

def fid_to_ynab4(tx):
    payee = tx.normalize_payee(tx.get_payees())
    memo = tx.generate_ynab4_memo()
    return Transaction_YNAB4(tx.date, payee, None, memo, None, tx.amount)

def generate_ynabcsv_fidelity(raw):
    # clean input data
    records = clean_raw_data(raw)

    # transform
    tx_fid = create_transactions_fid(records)
    tx_ynab4 = [fid_to_ynab4(tx) for tx in tx_fid]

    # output
    dstring = datetime.now().strftime('%Y%m%d') #YYYYMMDD
    with open(f'ynab-import_{dstring}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(generate_ynab4_header())
        writer.writerows(tx_ynab4)

if __name__ == '__main__':
    # read from clipboard
    generate_ynabcsv_fidelity(Tk().clipboard_get())
    