from datetime import timedelta
from src.patterns.base_detector import BasePatternDetector
from src.clustering.network_builder import NetworkBuilder
from src.models.ring_detail import RingDetail
from typing import Dict, Any

class DispersalDetector(BasePatternDetector):
    # Tunable parameters
    CHAIN_LENGTH = 3
    UNIQUE_THRESHOLD = 5
    TIME_LIMIT = timedelta(hours=1)
    BASE_SUSPICION = 70.0

    def __init__(self, accounts: Dict[str, Any], adjacency_list: Dict[str, Any], reverse_adjacency_list: Dict[str, Any], network_builder: NetworkBuilder = None):
        super().__init__(accounts, adjacency_list, reverse_adjacency_list)
        self.network_builder = network_builder

    def detect(self):
        print("Detecting dispersal patterns (Fan-Out/Fan-In) with Burst BFS...")
        self._detect_fan()

    def _detect_fan(self):
        # Fan-Out: One sender -> Many receivers
        # Use adj_list, look for Unique Receivers > Threshold
        for account_id, profile in self.accounts.items():
            if "payroll" in profile.tags or "merchant" in profile.tags:
                continue
            if len(profile.unique_receivers) > self.UNIQUE_THRESHOLD:
                self._bfs_burst(account_id, self.adjacency_list, "ringtype:dispersal_fan_out", is_fan_out=True)
            if len(profile.unique_senders) > self.UNIQUE_THRESHOLD:
                self._bfs_burst(account_id, self.reverse_adjacency_list, "ringtype:dispersal_fan_in", is_fan_out=False)


    def _bfs_burst(self, start_node: str, adj: dict, tag_name: str, is_fan_out: bool):
        # BFS State: (current_node, depth)
        queue = [(start_node, 0)]
        visited_in_sequence = set()
        visited_in_sequence.add(start_node)
        self.accounts[start_node].IncSuspiciousScore(100)
        
        while queue:
            curr, depth = queue.pop(0)
            
            if depth >= self.CHAIN_LENGTH:
                break

            if curr not in adj:
                continue

            # 1. Identify Burst Edges from current node
            edges = adj[curr]
            # Ensure chronological order for burst check
            edges.sort(key=lambda x: x['timestamp'])

            burst_neighbors = set()
            
            # Check consecutive transactions for TIMELIMIT constraint
            # A burst is a sequence of txs close in time.
            # Any tx involved in a burst is valid for traversal.
            
            # We need to look at windows. 
            # If t2-t1 <= Limit, both t1 and t2 are in burst.
            
            # Optimization: boolean array or set of indices
            in_burst = [False] * len(edges)
            
            for i in range(1, len(edges)):
                t_prev = edges[i-1]['timestamp']
                t_curr = edges[i]['timestamp']
                
                if t_curr - t_prev <= self.TIME_LIMIT:
                    in_burst[i-1] = True
                    in_burst[i] = True
            


            # If no bursts found at this node, chain stops here for this path
            if not any(in_burst):
                continue
                
            # Score this node for being part of a burst chain
            # Diminishing score based on depth
            score_boost = self.BASE_SUSPICION / (depth + 1)
            self.accounts[curr].IncSuspiciousScore(score_boost)
            
            if tag_name not in self.accounts[curr].tags:
                self.accounts[curr].tags.append(tag_name)
            
            # Collect neighbors for next level BFS
            neighbor_key = 'receiver' if is_fan_out else 'sender'
            
            for i, is_active in enumerate(in_burst):
                if is_active:
                    neighbor = edges[i][neighbor_key]
                    if neighbor not in visited_in_sequence:
                        visited_in_sequence.add(neighbor)
                        queue.append((neighbor, depth + 1))
                        burst_neighbors.add(neighbor)

            # Optimization: If fan-out/in is huge, queue might get large. 
            # visited_in_sequence prevents cycles and redundant work.

        if self.network_builder and len(visited_in_sequence) > 1:
            members = list(visited_in_sequence)
            ring_id = f"DISPERSAL_{start_node}"
            # Simple structure: all members in one group for now as specific depth tracking requires refactor
            nodes_by_distance = [members] 
            
            detail = RingDetail(
                ring_id=ring_id,
                members=members,
                nodes_by_distance=nodes_by_distance
            )
            self.network_builder.built_networks(ring_id, detail)
