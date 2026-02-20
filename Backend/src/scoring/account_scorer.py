from typing import Dict
from src.models.account_profile import AccountProfile

class AccountScorer:
    def __init__(self, accounts: Dict[str, AccountProfile]):
        self.accounts = accounts
        

    def score_accounts(self):
        print("Calculating final account suspicious scores...")
        for account_id, profile in self.accounts.items():
            
            if profile.total_sent > 10000: # Arbitrary threshold
                 profile.suspicious_score += 15

            if (abs(profile.total_received - profile.total_sent)/(profile.total_sent + 1)) >0.12 :
                profile.suspicious_score += 30

            profile.suspicious_score += profile.bursts * 12

            if profile.suspicious_score >= 300:
                profile.suspicious_score = 293
            
            if profile.suspicious_score < 20:
                profile.suspicious_score = 0.1
            else:
              profile.suspicious_score = profile.suspicious_score / 300 *100

            
    
    
   