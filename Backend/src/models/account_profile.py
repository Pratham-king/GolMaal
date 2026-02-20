from dataclasses import dataclass, field
from typing import List, Set, Optional
from datetime import datetime

@dataclass
class AccountProfile:
    account_id: str
    total_sent: float = 0.0
    total_received: float = 0.0
    unique_senders: Set[str] = field(default_factory=set)
    unique_receivers: Set[str] = field(default_factory=set)
    first_seen_time: Optional[datetime] = None
    last_seen_time: Optional[datetime] = None
    transaction_count: int = 0
    suspicious_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    network_id: Optional[str] = None
    bursts: int = 0

    def update(self, amount: float, is_sender: bool, counterparty: str, timestamp: datetime):
        self.transaction_count += 1
        
        if self.first_seen_time is None or timestamp < self.first_seen_time:
            self.first_seen_time = timestamp
        if self.last_seen_time is None or timestamp > self.last_seen_time:
            self.last_seen_time = timestamp

        if is_sender:
            self.total_sent += amount
            self.unique_receivers.add(counterparty)
        else:
            self.total_received += amount
            self.unique_senders.add(counterparty)

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "total_sent": self.total_sent,
            "total_received": self.total_received,
            "unique_senders_count": len(self.unique_senders),
            "unique_receivers_count": len(self.unique_receivers),
            "first_seen_time": self.first_seen_time.isoformat() if self.first_seen_time else None,
            "last_seen_time": self.last_seen_time.isoformat() if self.last_seen_time else None,
            "transaction_count": self.transaction_count,
            "suspicious_score": self.suspicious_score,
            "tags": self.tags,
            "network_id": self.network_id
        }
    def IncSuspiciousScore(self, amount):
        self.suspicious_score += amount
    def UpdateBurstCount(self):
        self.bursts += 1