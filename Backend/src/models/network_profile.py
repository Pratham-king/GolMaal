from dataclasses import dataclass, field
from typing import List

@dataclass
class NetworkProfile:
    network_id: str
    members: List[str] = field(default_factory=list)
    total_amount_moved: float = 0.0
    pattern_types_present: List[str] = field(default_factory=list)
    avg_suspicious_score: float = 0.0
    risk_score: float = 0.0
    risk_level: str = "Low"

    def to_dict(self):
        return {
            "network_id": self.network_id,
            "members": self.members,
            "member_count": len(self.members),
            "total_amount_moved": self.total_amount_moved,
            "patterns": self.pattern_types_present,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level
        }
