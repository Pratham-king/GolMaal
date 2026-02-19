from typing import List, Dict, Set
from src.models.account_profile import AccountProfile
from src.models.network_profile import NetworkProfile

class NetworkBuilder:
    def __init__(self, accounts: Dict[str, AccountProfile], adjacency_list: Dict[str, List[Dict]]):
        self.accounts = accounts
        self.adjacency_list = adjacency_list
        self.networks: List[NetworkProfile] = []

    def build_networks(self) -> List[NetworkProfile]:
        print("Building suspicious networks (clustering)...")
        # heuristic: only cluster accounts with some suspicion
        suspicious_accounts = [
            acc_id for acc_id, profile in self.accounts.items() 
            if profile.suspicious_score > 0
        ]
        
        visited: Set[str] = set()
        network_counter = 0

        for account_id in suspicious_accounts:
            if account_id not in visited:
                network_counter += 1
                network_id = f"N{network_counter:03d}"
                members = self._bfs_cluster(account_id, visited, suspicious_accounts)
                
                # Update profiles with network_id
                for member_id in members:
                    self.accounts[member_id].network_id = network_id

                # Create Network Profile
                network_profile = NetworkProfile(
                    network_id=network_id,
                    members=members
                )
                self.networks.append(network_profile)
        
        print(f"Formed {len(self.networks)} suspicious networks.")
        return self.networks

    def _bfs_cluster(self, start_node: str, visited: Set[str], allowed_nodes: List[str]) -> List[str]:
        cluster = []
        queue = [start_node]
        visited.add(start_node)
        allowed_set = set(allowed_nodes)

        while queue:
            node = queue.pop(0)
            cluster.append(node)
            
            # check neighbors
            if node in self.adjacency_list:
                for edge in self.adjacency_list[node]:
                    neighbor = edge['receiver']
                    if neighbor in allowed_set and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            # In a real graph, we should also check incoming edges for clustering (weakly connected components)
            # For this demo, we use the graph builder's reverse list if available, or just traverse forward.
            # Assuming undirected connectivity for clustering usually makes sense for "networks".
        
        return cluster
