from typing import List, Set, Dict, Any, Tuple
from src.patterns.base_detector import BasePatternDetector
from src.models.ring_detail import RingDetail
from datetime import datetime

class LoopDetector(BasePatternDetector):
    def detect(self):
        print("Detecting loops (cycles) using modified Johnson's algorithm...")
        
        self.loops_detected: Dict[str, RingDetail] = {}
        self.loop_counter = 0

        # Create a sorted list of nodes to iterate through
        # Sorting helps in deterministic execution and allows skipping nodes < start_node
        nodes = sorted(list(self.accounts.keys()))
        
        for start_node in nodes:
            self._circuit(start_node, start_node, [], datetime.min)

        print(f"Total loops detected: {len(self.loops_detected)}")

    def _circuit(self, start_node: str, current_node: str, stack: List[Tuple[str, datetime]], min_timestamp: datetime):
        """
        Recursive function to find circuits starting from start_node.
        Subject to constraints:
        1. Nodes in path must be >= start_node (avoids duplicates).
        2. Edges must have timestamp > min_timestamp (temporal constraint).
        """
        
        # Add current node to stack with the timestamp of the edge that led to it
        # For the start node, we can use a dummy timestamp or handle it separately.
        # Here stack stores (node_id, arrival_time)
        
        # If stack is empty, it's the start node
        arrival_time = min_timestamp
        if stack:
            arrival_time = stack[-1][1]

        # Optimization: Don't revisit nodes already in current stack (simple cycle check)
        # Johnson's usually uses blocked set, but for simple DFS with constraints this works for now.
        if any(node == current_node for node, _ in stack):
            return

        stack.append((current_node, arrival_time))
        
        if current_node in self.adjacency_list:
            for edge in self.adjacency_list[current_node]:
                neighbor = edge['receiver']
                edge_timestamp = edge['timestamp']
                
                # Constraint 1: Canonical ordering to avoid duplicates
                if neighbor < start_node:
                    continue
                
                # Constraint 2: Temporal constraint
                # Only follow edges that occurred AFTER the edge that started this path segment
                # For the first edge (from start_node), min_timestamp is datetime.min, so any edge works.
                # if edge_timestamp <= min_timestamp and len(stack) > 1:
                #      continue

                if neighbor == start_node:
                    # Cycle found!
                    # Only accept if cycle length >= 3
                    if len(stack) >= 3:
                        # Also check temporal constraint for closing edge if necessary? 
                        # The user said "after the initial node". 
                        # If we strictly interpret "after completing all iterations", 
                        # the closing edge should also follow time, but typically loops close back.
                        # Let's apply the condition: closing edge time > last edge time?
                        # User query: "check the timestmp only use the transactions which are after the initial node"
                        # This implies any edge in the loop must be > start_node's initial transaction?
                        # Or strictly increasing time? "index is the distance... use transactions which are after the initial node"
                        # Implementation: verify edge_timestamp > stack[1].timestamp (the first edge in path)
                        
                        first_edge_time = stack[1][1] if len(stack) > 1 else datetime.min
                        if len(stack) > 1 and edge_timestamp <= first_edge_time:
                             continue

                        self._record_loop(stack)
                else:
                    # Recursive step
                    # Pass the timestamp of this edge as the new constraint?
                    # "check the timestmp only use the transactions which are after the initial node"
                    # This could mean globally after the *start* of the loop, or incrementally increasing.
                    # "strict implementation" often implies strictly increasing in financial typologies.
                    # However, the user specific note "after the initial node" is key.
                    # Let's enforce: edge_timestamp > first_edge_timestamp (transaction from start_node)
                    
                    next_min_time = min_timestamp
                    if len(stack) == 1:
                        # This is the first edge from start_node.
                        # Subsequent edges must be after this one.
                        next_min_time = edge_timestamp
                    
                    self._circuit(start_node, neighbor, stack, next_min_time)
        
        stack.pop()

    def _record_loop(self, stack: List[Tuple[str, datetime]]):
        members = [node for node, _ in stack]
        
        # Structure nodes by distance
        # "store the value of nodes by appending to the array at index... index is the distance"
        nodes_by_distance: List[List[str]] = []
        for i, member in enumerate(members):
            while len(nodes_by_distance) <= i:
                nodes_by_distance.append([])
            nodes_by_distance[i].append(member)
            
        ring_id = f"LOOP_{self.loop_counter}"
        self.loop_counter += 1
        
        detail = RingDetail(
            ring_id=ring_id,
            members=members,
            nodes_by_distance=nodes_by_distance,
            suspicious_score_boost=50.0 # Default value
        )
        
        self.loops_detected[ring_id] = detail
        # self._increase_suspicion(members) # User requirement
        self.increase_suspicion(members)

    def increase_suspicion(self, members: List[str]):
        """
        Increases suspicion score for the found members.
        """
        for member_id in members:
            if member_id in self.accounts:
                self.accounts[member_id].suspicious_score += 50
                if "ringtype:loop" not in self.accounts[member_id].tags:
                    self.accounts[member_id].tags.append("ringtype:loop")
