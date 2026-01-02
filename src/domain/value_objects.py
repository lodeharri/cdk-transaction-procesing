from dataclasses import dataclass
from enum import Enum

class TransactionStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "COP"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("El monto no puede ser negativo")