from typing import List, Dict
from src.models.network_profile import NetworkProfile
from src.models.account_profile import AccountProfile

class RiskEngine:
    def __init__(self, networks: List[NetworkProfile], accounts: Dict[str, AccountProfile]):
        self.networks = networks
        self.accounts = accounts

    def evaluate_network_risk(self):
        print("Evaluating network risks...")
        for network in self.networks:
            member_scores = [self.accounts[m].suspicious_score for m in network.members]
            avg_score = sum(member_scores) / len(member_scores) if member_scores else 0
            
            # Pattern diversity
            all_patterns = set()
            total_volume = 0
            shell_count = 0
            
            for m in network.members:
                profile = self.accounts[m]
                total_volume += profile.total_sent + profile.total_received
                for tag in profile.tags:
                    all_patterns.add(tag)
                if "ringtype:shell" in profile.tags:
                    shell_count += 1
            
            pattern_diversity_score = len(all_patterns) * 10
            
            # Simple volume scaling (logarithmic in real life, linear here for demo)
            volume_score = min(total_volume / 10000, 20) 
            
            network.risk_score = (avg_score * 0.5) + pattern_diversity_score + volume_score + (shell_count * 10)
            network.total_amount_moved = total_volume
            network.pattern_types_present = list(all_patterns)
            network.avg_suspicious_score = avg_score

            # Categorize
            if network.risk_score > 80:
                network.risk_level = "Critical"
            elif network.risk_score > 60:
                network.risk_level = "High"
            elif network.risk_score > 30:
                network.risk_level = "Medium"
            else:
                network.risk_level = "Low"
