from typing import List, Dict, Set
from src.models.account_profile import AccountProfile
from src.models.network_profile import NetworkProfile
from src.models.ring_detail import RingDetail

class NetworkBuilder:
    def __init__(self, accounts: Dict[str, AccountProfile], adjacency_list: Dict[str, List[Dict]]):
        self.accounts = accounts
        self.adjacency_list = adjacency_list
        self.networks: List[NetworkProfile] = []

    def built_networks(self, name: str, detail: RingDetail) :
        self.networks.append(NetworkProfile(network_id=name, members=detail.members))

    
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
