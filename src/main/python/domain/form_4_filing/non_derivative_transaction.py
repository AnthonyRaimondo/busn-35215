from domain.transaction import Transaction


class NonDerivativeTransaction(Transaction):
    def __init__(self, transaction_code: str, number_of_shares: float, shares_held_following_transaction: float,
                 share_price: float):
        super().__init__(transaction_code, number_of_shares, shares_held_following_transaction, share_price)
