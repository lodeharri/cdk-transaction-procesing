import uuid
from domain.value_objects import Money, TransactionStatus

class Transaction:
    def __init__(self, amount: Money, merchant_id: str, idempotency_key: str, correlation_id: str):
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.merchant_id = merchant_id
        self.idempotency_key = idempotency_key
        self.status = TransactionStatus.PENDING
        self.correlation_id = correlation_id

    def approve(self):
        self.status = TransactionStatus.APPROVED

    def reject(self):
        self.status = TransactionStatus.REJECTED