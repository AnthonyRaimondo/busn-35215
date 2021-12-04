from typing import List

from domain.form_4_filing.company import Company
from domain.form_4_filing.derivative_transaction import DerivativeTransaction
from domain.form_4_filing.non_derivative_transaction import NonDerivativeTransaction
from domain.form_4_filing.shareholder import Shareholder


class FilingTransactions:
    def __init__(self, company: Company, shareholder: Shareholder,
                 non_derivative_transactions: List[NonDerivativeTransaction],
                 derivative_transactions: List[DerivativeTransaction] = None):
        self.company: Company = company
        self.shareholder: Shareholder = shareholder
        self.non_derivative_transactions: List[NonDerivativeTransaction] = non_derivative_transactions
        self.derivative_transactions: List[DerivativeTransaction] = derivative_transactions
