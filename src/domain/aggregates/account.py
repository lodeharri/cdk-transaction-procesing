class Account:
    def __init__(self, merchant_id: str, is_active: bool, balance: float):
        self.merchant_id = merchant_id
        self.is_active = is_active
        self.balance = balance

    def can_receive_payments(self) -> bool:
        return self.is_active