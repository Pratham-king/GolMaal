from src.patterns.base_detector import BasePatternDetector

class ShellDetector(BasePatternDetector):
    def detect(self):
        print("Detecting shell accounts...")
        for account_id, profile in self.accounts.items():
            if not profile.first_seen_time or not profile.last_seen_time:
                continue

            lifecycle_days = (profile.last_seen_time - profile.first_seen_time).days
            
            # Criteria
            short_lifecycle = lifecycle_days < 3
            few_transactions = profile.transaction_count < 10
            balanced_flow = False
            
            if profile.total_received > 0:
                balance_ratio = abs(profile.total_sent - profile.total_received) / profile.total_received
                if balance_ratio < 0.1: # 10% difference means mostly pass-through
                    balanced_flow = True
            
            if short_lifecycle and few_transactions and balanced_flow:
                profile.suspicious_score += 60
                if "ringtype:shell" not in profile.tags:
                    profile.tags.append("ringtype:shell")
