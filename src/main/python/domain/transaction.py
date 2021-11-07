from abc import ABC


class Transaction(ABC):
    def __init__(self, transaction_code: str, number_of_shares: float, shares_held_following_transaction: float,
                 share_price: float):
        self.transaction_code: str = transaction_code
        self.number_of_shares: float = number_of_shares
        self.shares_held_following_transaction: float = shares_held_following_transaction
        self.share_price: float = share_price
