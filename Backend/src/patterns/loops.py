from typing import List, Set
from src.patterns.base_detector import BasePatternDetector

class LoopDetector(BasePatternDetector):
    def detect(self):
        print("Detecting loops (cycles)...")
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()
        path_stack: List[str] = []
        
        # Simple DFS for cycle detection
        # strict implementation of Tarjan's or Johnson's would be better for all cycles, 
        # but simple DFS is good for a start to find *some* cycles.
        
        # For a more robust approach in a real system, we'd want to find elementary circuits.
        # Here we will implement a DFS that looks for back-edges to the recursion stack.
        
        def dfs(node: str, current_path: List[str], current_stack: Set[str]):
            visited.add(node)
            current_stack.add(node)
            current_path.append(node)
            
            if node in self.adjacency_list:
                for edge in self.adjacency_list[node]:
                    neighbor = edge['receiver']
                    if neighbor not in visited:
                        dfs(neighbor, current_path, current_stack)
                    elif neighbor in current_stack:
                        # Cycle found!
                        # Extract the cycle from the path
                        try:
                            start_index = current_path.index(neighbor)
                            cycle = current_path[start_index:]
                            if len(cycle) >= 3:
                                self._mark_suspicious(cycle)
                        except ValueError:
                            pass
            
            current_stack.remove(node)
            current_path.pop()

        for account_id in self.accounts:
            if account_id not in visited:
                dfs(account_id, [], set())
    
    def _mark_suspicious(self, cycle: List[str]):
        # print(f"Loop detected: {cycle}")
        for account_id in cycle:
            profile = self.accounts[account_id]
            profile.suspicious_score += 50
            if "ringtype:loop" not in profile.tags:
                profile.tags.append("ringtype:loop")
            # In a real system, we would assign a unique network ID here or in the clustering phase
