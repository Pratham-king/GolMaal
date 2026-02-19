import json
from typing import Dict, List
from src.models.account_profile import AccountProfile
from src.models.network_profile import NetworkProfile
from src.models.ring_detail import RingDetail

class JsonExporter:
    SUSPICIOUS_THRESHOLD = 30

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
                acc_type = "Disperse"
            
            # Create account object
            acc_data = {
                "Account_id": acc.account_id,
                "Reciving Edges": list(acc.unique_senders),
                "sending Edges": list(acc.unique_receivers),
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
    def export_download_report(accounts: Dict[str, AccountProfile], networks: List[NetworkProfile], loops: Dict[str, RingDetail], processing_time: str, output_file: str):
        # 1. Suspicious Accounts
        suspicious_accounts = []
        for acc in accounts.values():
            if acc.suspicious_score >= JsonExporter.SUSPICIOUS_THRESHOLD:
                suspicious_accounts.append({
                    "Account_id": acc.account_id,
                    "Suspicious_score": acc.suspicious_score,
                    "detected_patterns": acc.tags,
                    "Ring_id": acc.network_id if acc.network_id else "N/A"
                })
        
        # Sort desc by score
        suspicious_accounts.sort(key=lambda x: x["Suspicious_score"], reverse=True)

        # 2. Fraud Rings
        fraud_rings = []
        for net in networks:
            fraud_rings.append({
                "Ring_id": net.network_id,
                "Members": net.members,
                "risk": net.risk_score
            })
            
        # 3. Summary
        summary = {
            "Accounts_Anaylsed": len(accounts),
            "Suspicious_Account": len(suspicious_accounts),
            "Rings_detected": len(networks),
            "Processing_time": processing_time
        }

        output_data = {
            "Suspicious account": suspicious_accounts,
            "Fraud Ring": fraud_rings,
            "Summary": summary
        }

        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Exported download report to {output_file}")
        except Exception as e:
            print(f"Error exporting download report: {e}")
