from datetime import timedelta
from typing import Dict, List, Any
from src.patterns.base_detector import BasePatternDetector
import numpy as np

class MerchantDetector(BasePatternDetector):
    # Tunable parameters

    def detect(self):
        print("Detecting Merchant accounts...")

        # Avg Transctions value

          
        # Pre-calculate counts for efficiency and to find max
        
        for account_id, profile in self.accounts.items():
            # Incoming transactions count

            if account_id in self.reverse_adjacency_list:
                incoming_count = len(self.reverse_adjacency_list[account_id])
            else:
                incoming_count = 0
            
            # Outgoing transactions count
            
            if account_id in self.adjacency_list:
                outgoing_count = len(self.adjacency_list[account_id])
            else:
                outgoing_count = 0
            
            max_trx = incoming_count + outgoing_count
            
            # unique_senders is already in profile
            senders = len(profile.unique_senders) 
            recivers  = len(profile.unique_receivers)
            max_acc = senders + recivers
            
        
            if max_trx <= 15 or senders <= 2 or recivers <= 2:
                continue
            
            if self.accounts[account_id].last_seen_time - self.accounts[account_id].first_seen_time < timedelta(days=15): 
                continue
            # S_m = (w1 * (count / max_trx) + w2 * (distinct / max_senders)) * 100
            
            volume = (self.accounts[account_id].total_sent - self.accounts[account_id].total_received)/(self.accounts[account_id].total_sent + self.accounts[account_id].total_received)
                
            if volume < 0.15 or volume > 0.35 :
                continue

            variance = np.std(self.adjacency_list[account_id]+self.reverse_adjacency_list[account_id])
            
            if variance < 70 :
                continue
            
            self.accounts[account_id].tags = ["merchant"]
            self.accounts[account_id].suspicious_score = 0 
        return