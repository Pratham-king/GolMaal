from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: datetime

    def to_dict(self):
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat()
        }
