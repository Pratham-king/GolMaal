import json
from typing import Dict, List
from src.models.account_profile import AccountProfile
from src.models.network_profile import NetworkProfile
from src.models.ring_detail import RingDetail

class JsonExporter:
    SUSPICIOUS_THRESHOLD = 10

    @staticmethod
    def export(accounts: Dict[str, AccountProfile], networks: List[NetworkProfile], output_file: str):
        account_list = []
        for acc in accounts.values():
            # Determine type
            acc_type = "None"
            tags = set(acc.tags)
            if "ringtype:loop" in tags:
                acc_type = "Loop"
            elif "ringtype:shell" in tags:
                acc_type = "Shell"
            elif "ringtype:dispersal_fan_out" in tags or "ringtype:dispersal_fan_in" in tags:
                acc_type = "Smurf"
            elif "payroll" in tags:
                acc_type = "Payroll"
            elif "Merchant" in tags:
                acc_type = "Merchant"
            
            # Create account object
            acc_data = {
                "Account_id": acc.account_id,
                "Reciving Edges": list(acc.unique_senders),
                "sending Edges": list(acc.unique_receivers),
                "suspicion_score": round(acc.suspicious_score, 3),
                "type": acc_type
            }
            account_list.append(acc_data)

        output_data = {
            "accounts": account_list,
            "networks": [net.to_dict() for net in networks]
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Exported results to {output_file}")
        except Exception as e:
            print(f"Error exporting JSON: {e}")

    @staticmethod
    def export_download_report(accounts: Dict[str, AccountProfile], networks: List[NetworkProfile], loops: Dict[str, RingDetail], 
                             processing_time: str, output_file: str, 
                             adj_list: Dict[str, List[Dict]], rev_adj_list: Dict[str, List[Dict]]):
        # 1. Suspicious Accounts
        suspicious_accounts = []
        for acc in accounts.values():
            if acc.suspicious_score >= JsonExporter.SUSPICIOUS_THRESHOLD:
                # Determine type
                acc_type = "None"
                tags = set(acc.tags)
                if "payroll" in tags:
                    acc_type = "Payroll"
                elif "ringtype:loop" in tags:
                    acc_type = "Loop"
                elif "ringtype:shell" in tags:
                    acc_type = "Shell"
                elif "ringtype:dispersal_fan_out" in tags or "ringtype:dispersal_fan_in" in tags:
                    acc_type = "Smurf"

                # Get edges from adj lists
                # adj_list[acc_id] -> list of dicts with 'receiver' key -> sending Edges
                sending_edges = []
                if acc.account_id in adj_list:
                    sending_edges = [edge['receiver'] for edge in adj_list[acc.account_id]]
                
                # rev_adj_list[acc_id] -> list of dicts with 'sender' key -> Reciving Edges
                receiving_edges = []
                if acc.account_id in rev_adj_list:
                    receiving_edges = [edge['sender'] for edge in rev_adj_list[acc.account_id]]

                if acc.suspicious_score < 20:
                    continue

                suspicious_accounts.append({
                    "account_id": acc.account_id,
                    "suspicion_score": round(acc.suspicious_score, 3),
                    "detected_patterns": acc.tags,
                    "ring_id": acc.network_id if acc.network_id else "N/A",
                    "Reciving Edges": list(set(receiving_edges)), # Unique
                    "sending Edges": list(set(sending_edges)),    # Unique
                    "type": acc_type
                })
        
        # Sort desc by score
        suspicious_accounts.sort(key=lambda x: x["suspicion_score"], reverse=True)
        fraud_ring_count = 0
        # 2. Fraud Rings
        fraud_rings = []
        for net in networks:
            net_pattern = "None"
            if net.pattern_types_present == []:
                continue
            else:
                fraud_ring_count += 1
            if "payroll" in net.pattern_types_present:
                net_pattern = "Payroll"
            elif "ringtype:loop" in net.pattern_types_present:
                net_pattern = "Loop"
            elif "ringtype:shell" in net.pattern_types_present:
                net_pattern = "Shell"
            elif "ringtype:dispersal_fan_out" in net.pattern_types_present or "ringtype:dispersal_fan_in" in net.pattern_types_present:
                net_pattern = "Smurf"
            
            fraud_rings.append({
                "ring_id": net.network_id,
                "member_accounts": net.members,
                "pattern_type" : net_pattern,
                "risk_score" : round(net.risk_score, 3)
            })
            
        # 3. Summary
        

        summary = {
            "total_accounts_analyzed": len(accounts),
            "suspicious_accounts_flagged": len(suspicious_accounts),
            "fraud_rings_detected": fraud_ring_count,
            "processing_time_seconds": processing_time
        }

        output_data = {
            "suspicious_accounts": suspicious_accounts,
            "fraud_rings": fraud_rings,
            "summary": summary
        }

        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Exported download report to {output_file}")
        except Exception as e:
            print(f"Error exporting download report: {e}")
