# fidelity-to-ynab
Converts Fidelity 401(k) transactions on the clipboard to a YNAB import csv file

Navigate to the transaction history section of your Fidelity 401(k) plan, and select the 'Sources tab'.
Then, copy the data you would like to transform to a YNAB4 csv, as seen in the image below. Do not include the Fidelity Header on your clipboard.

You will then need to run the ```generate_ynabcsv_fidelity.py``` file using whatever method you like on your system.

![Fidelity 401(k) Transaction History, by source](https://user-images.githubusercontent.com/49046440/202799647-d5350da8-be95-4c71-adda-b3ffaa16fe36.png)



The output will be the a YNAB4 csv file, ready for import with the following headers:

* Date
* Payee
* Category
* Memo
* Outflow
* Inflow

The output of the data from the above screenshot is the following, which can then be imported using YNAB4's import functionality:

![Output csv for YNAB4 displayed in Microsoft Excel](https://user-images.githubusercontent.com/49046440/202799724-49714b5a-3017-41dd-8d0c-1ba464a0ae60.png)

![YNAB4 import functionality](https://user-images.githubusercontent.com/49046440/202800025-5969e0b7-6a52-4987-ad6a-bd9400196fe4.png)


# Making changes
If you would like to change the payee for which different Fidelity transactions are mapped, you will need to update the ```get_payees``` and ```normalize_payees``` methods of the ```Transaction_fid``` class.

The YNAB4 memo is generated in the ```Transaction_fid``` class's ```generate_ynab4_memo``` method.

# Compatibility
Written with Python 3.9.4, but no packages except base should be required, and I think it will work with any Python 3 distribution.
