from typing import Dict
from src.models.account_profile import AccountProfile

class AccountScorer:
    def __init__(self, accounts: Dict[str, AccountProfile]):
        self.accounts = accounts

    def score_accounts(self):
        print("Calculating final account suspicious scores...")
        for account_id, profile in self.accounts.items():
            # Base score is already accumulated by pattern detectors
            # Here we can add global normalization or extra weights
            
            # Example: Bonus for multiple pattern types
            unique_patterns = set()
            for tag in profile.tags:
                if tag.startswith("ringtype:"):
                    unique_patterns.add(tag)
            
            if len(unique_patterns) > 1:
                profile.suspicious_score += 25 # Repeated pattern bonus
            
            # High amount anomaly (simplified)
            if profile.total_sent > 100000: # Arbitrary threshold
                 profile.suspicious_score += 30

            # Cap or Normalize if needed
            # profile.suspicious_score = min(profile.suspicious_score, 100)
