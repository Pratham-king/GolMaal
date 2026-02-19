from dataclasses import dataclass, field
from typing import List

@dataclass
class RingDetail:
    ring_id: str
    members: List[str]
    nodes_by_distance: List[List[str]]
    suspicious_score_boost: float = 0.0

    def to_dict(self):
        return {
            "ring_id": self.ring_id,
            "members": self.members,
            "nodes_by_distance": self.nodes_by_distance,
            "suspicious_score_boost": self.suspicious_score_boost
        }
