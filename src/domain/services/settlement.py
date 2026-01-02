from domain.aggregates.transaction import Transaction
from domain.aggregates.account import Account

class SettlementService:
    @staticmethod
    def evaluate_transaction(transaction: Transaction, account: Account):
        # Regla: No se procesan transacciones si la cuenta del comercio está inactiva
        if not account.can_receive_payments():
            transaction.reject()
            return False
        
        transaction.approve()
        return True