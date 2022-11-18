import csv
import re
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
            return ':'.join([self.date, self.source, self.transaction_type])
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

def separate_cols(records):
    '''
    Each record is a tab-delimited list. Explicitly create a list by separating on tabs
    Order of data: [date, source, transaction type, cost, count of shares]
    '''

    # non-list comprehension
    records2 = records.copy()
    for i in range(0, len(records2)):
        records2[i] = records2[i].split('\t')
        for j in range(0, len(records2[i])):
            records2[i][j] = records2[i][j].strip()

    #records = [record.split('\t') for record in records]
    # TODO: convert to list comprehension
    #return [x.strip() for record in records for x in record.split('\t')]
    return records2

def create_transactions_fid(records):
    return [Transaction_fid(*record[:-1]) for record in records]

def fid_to_ynab4(tx):
    payee = tx.normalize_payee(tx.get_payees())
    memo = tx.generate_ynab4_memo()
    return Transaction_YNAB4(tx.date, payee, None, memo, None, tx.amount)

def generate_ynabcsv_fidelity(raw):
    no_details = remove_showdetails(raw)
    records = no_details.split('\n')
    records = separate_cols(records)
    tx_fid = create_transactions_fid(records)
    tx_ynab4 = [fid_to_ynab4(tx) for tx in tx_fid]
    with open('ynab_import.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(generate_ynab4_header())
        writer.writerows(tx_ynab4)

if __name__ == '__main__':
    # read from clipboard
    raw = Tk().clipboard_get()
    generate_ynabcsv_fidelity(raw)
    