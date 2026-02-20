from src.patterns.base_detector import BasePatternDetector
from src.clustering.network_builder import NetworkBuilder
from src.models.ring_detail import RingDetail
from typing import Dict, Any

class ShellDetector(BasePatternDetector):
    def __init__(self, accounts: Dict[str, Any], adjacency_list: Dict[str, Any], network_builder: NetworkBuilder = None):
        super().__init__(accounts, adjacency_list)
        self.network_builder = network_builder
    def detect(self):
        print("Detecting shell accounts...")
        for account_id, profile in self.accounts.items():
            if not profile.first_seen_time or not profile.last_seen_time:
                continue

            lifecycle_days = (profile.last_seen_time - profile.first_seen_time).days
            
            # Criteria
            short_lifecycle = lifecycle_days < 3
            few_transactions = profile.transaction_count < 2
            balanced_flow = False
            
            if profile.total_received > 0:
                balance_ratio = abs(profile.total_sent - profile.total_received) / profile.total_received
                if balance_ratio < 0.1: # 10% difference means mostly pass-through
                    balanced_flow = True
            
            if short_lifecycle and few_transactions and balanced_flow:
                profile.IncSuspiciousScore(60.0)
                if "ringtype:shell" not in profile.tags:
                    profile.tags.append("ringtype:shell")
                
                if self.network_builder:
                    ring_id = f"SHELL_{account_id}"
                    members = [account_id]
                    nodes_by_distance = [members]
                    
                    detail = RingDetail(
                        ring_id=ring_id,
                        members=members,
                        nodes_by_distance=nodes_by_distance
                    )
                    self.network_builder.built_networks(ring_id, detail)
