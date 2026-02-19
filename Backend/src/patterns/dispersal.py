from datetime import timedelta
from src.patterns.base_detector import BasePatternDetector

class DispersalDetector(BasePatternDetector):
    def detect(self):
        print("Detecting dispersal patterns (Fan-Out/Fan-In)...")
        self._detect_fan_out()
        self._detect_fan_in()

    def _detect_fan_out(self):
        # One account sends to many unique accounts in short window
        pass  # TODO: Implement sliding window logic
        # For simplicity in this structure setup, we'll do a basic check on the profile
        
        for account_id, profile in self.accounts.items():
            # Basic heuristic: High number of unique receivers
            if len(profile.unique_receivers) > 5: # Threshold example
                # Check time window (simplified)
                if profile.first_seen_time and profile.last_seen_time:
                    duration = (profile.last_seen_time - profile.first_seen_time).total_seconds() / 3600
                    if duration < 24 and duration > 0: # all within 24 hours
                         profile.suspicious_score += 40
                         if "ringtype:dispersal_fan_out" not in profile.tags:
                            profile.tags.append("ringtype:dispersal_fan_out")

    def _detect_fan_in(self):
        # Many accounts send to one
        for account_id, profile in self.accounts.items():
            if len(profile.unique_senders) > 5:
                 if profile.first_seen_time and profile.last_seen_time:
                    duration = (profile.last_seen_time - profile.first_seen_time).total_seconds() / 3600
                    if duration < 24 and duration > 0:
                         profile.suspicious_score += 40
                         if "ringtype:dispersal_fan_in" not in profile.tags:
                            profile.tags.append("ringtype:dispersal_fan_in")
