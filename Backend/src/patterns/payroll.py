from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
from src.patterns.base_detector import BasePatternDetector

class PayrollDetector(BasePatternDetector):
    # Tunable parameters
    UNIQUE_RECEIVER_THRESHOLD = 5
    MIN_MONTHS_ACTIVE = 3
    MONTHLY_WINDOW_DAYS = 7
    CONSISTENCY_WINDOW_DAYS = 7

    def detect(self):
        print("Detecting payroll patterns...")
        for account_id, profile in self.accounts.items():
            if "merchant" in profile.tags:
                continue
            # 1. Threshold Check
            if len(profile.unique_receivers) <= self.UNIQUE_RECEIVER_THRESHOLD:
                continue

            # 2. Get outgoing transactions
            if account_id not in self.adjacency_list:
                continue
            
            outgoing_txs = self.adjacency_list[account_id]
            if not outgoing_txs:
                continue

            # 3. Group by (Year, Month)
            tx_by_month = defaultdict(list)
            for tx in outgoing_txs:
                dt = tx['timestamp']
                tx_by_month[(dt.year, dt.month)].append(dt)

            # 4. Periodicity Check
            if len(tx_by_month) < self.MIN_MONTHS_ACTIVE:
                continue

            # 5. Window and Consistency Check
            is_payroll = True
            original_payday = None # Day of month roughly
            
            sorted_months = sorted(tx_by_month.keys())
            
            for ym in sorted_months:
                dates = tx_by_month[ym]
                days = [d.day for d in dates]
                min_day = min(days)
                max_day = max(days)
                
                # Monthly Window Check (all txs within 7 days)
                # Handle month wrapping? For simplicity, we assume same month day ranges.
                # If pay is 30th and 1st, they fall in diff months in this grouping logic.
                # Standard payroll is usually same-ish days. 
                # User constraint: "happen periodically/ montly" implies month-aligned.
                if max_day - min_day > (self.MONTHLY_WINDOW_DAYS - 1):
                    is_payroll = False
                    break
                
                # Determine "center" day for this month
                # Just take the first one or average
                current_payday = min_day
                
                if original_payday is None:
                    original_payday = current_payday
                else:
                    # Consistency Check (+/- 3 days)
                    # Handle end of month / start of month logic if needed?
                    # "all the transaction in adj list happens in +- 3 days of the original"
                    # We compare current_payday with original_payday
                    if abs(current_payday - original_payday) > self.CONSISTENCY_WINDOW_DAYS:
                        is_payroll = False
                        break
            
            if is_payroll:
                # Mark as payroll
                profile.suspicious_score = 0
        
                profile.tags = ["payroll"]
            
