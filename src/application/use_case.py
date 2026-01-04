from domain.aggregates.transaction import Transaction
from domain.value_objects import Money
from application.dtos import PaymentInputDTO

class ProcessPaymentUseCase:
    def __init__(self, repo, event_bus, settlement_service):
        self.repo = repo
        self.event_bus = event_bus
        self.settlement_service = settlement_service

    def execute(self, data: PaymentInputDTO):
        # 1. Obtener Cuenta del Comercio (Infra)
        account = self.repo.get_account(data.merchant_id)
        
        # 2. Crear Transacción (Dominio)
        transaction = Transaction(
            amount=Money(amount=data.amount),
            merchant_id=data.merchant_id,
            idempotency_key=data.idempotency_key,
            correlation_id=data.correlation_id
        )

        # 3. Validar con Servicio de Dominio (Unión de Agregados)
        self.settlement_service.evaluate_transaction(transaction, account)

        # 4. Si la idempotency_key ya existe, el repo lanzará una excepción
        self.repo.save_transaction(transaction)

        # 5. Publicar Evento si fue aprobada (EDA)
        # if is_approved:
        #     self.event_bus.publish("TransactionApproved", transaction.__dict__)

        return transaction