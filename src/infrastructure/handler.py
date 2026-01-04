import json
from pydantic import ValidationError
from application.dtos import PaymentInputDTO
from application.use_case import ProcessPaymentUseCase
from infrastructure.repositories import DynamoRepository
from infrastructure.event_bus import EventBridgeBus
from domain.services.settlement import SettlementService
import uuid

# Inyección de Dependencias (Ensamblaje manual)
repo = DynamoRepository()
bus = EventBridgeBus()
domain_service = SettlementService()
use_case = ProcessPaymentUseCase(repo, bus, domain_service)

def handler(event, context):
    try:
        # 1. Validación de entrada (Pydantic)
        body = json.loads(event.get("body", "{}"))
        correlation_id = event.get("headers", {}).get("x-correlation-id", str(uuid.uuid4()))

        body["correlation_id"] = correlation_id

        input_dto = PaymentInputDTO(**body)

        # 2. Ejecución del Caso de Uso
        result = use_case.execute(input_dto)

        return {
            "statusCode": 201,
            "body": json.dumps({"transaction_id": result.id, "status": result.status.value})
        }

    except ValueError as e:
        if "IDEMPOTENCY_ERROR" in str(e):
            return {
                "statusCode": 200, # Devolvemos 200 porque la transacción ya existe
                "body": json.dumps({
                    "message": "Esta transacción ya fue procesada anteriormente.",
                    "idempotency_key": str(e).split(": ")[1]
                })
            }
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        return {"statusCode": 409, "body": json.dumps({"error": str(e)})}