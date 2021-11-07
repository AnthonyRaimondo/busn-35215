from domain.transaction import Transaction


class DerivativeTransaction(Transaction):
    def __init__(self, transaction_code: str, number_of_shares: float, shares_held_following_transaction: float,
                 share_price: float, exercise_price: float):
        super().__init__(transaction_code, number_of_shares, shares_held_following_transaction, share_price)
        self.exercise_price: float = exercise_price
