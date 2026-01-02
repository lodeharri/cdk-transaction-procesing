from pydantic import BaseModel, Field

class PaymentInputDTO(BaseModel):
    merchant_id: str = Field(..., min_length=5)
    amount: float = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=10)