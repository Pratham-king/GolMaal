import json
from typing import Dict, List
from src.models.account_profile import AccountProfile
from src.models.network_profile import NetworkProfile

class JsonExporter:
    @staticmethod
    def export(accounts: Dict[str, AccountProfile], networks: List[NetworkProfile], output_file: str):
        output_data = {
            "accounts": [acc.to_dict() for acc in accounts.values() if acc.suspicious_score > 0],
            "networks": [net.to_dict() for net in networks]
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Exported results to {output_file}")
        except Exception as e:
            print(f"Error exporting JSON: {e}")
