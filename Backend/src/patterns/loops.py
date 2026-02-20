from typing import List, Dict, Any, Tuple
from src.patterns.base_detector import BasePatternDetector
from src.models.ring_detail import RingDetail
from src.clustering.network_builder import NetworkBuilder
from datetime import datetime

class LoopDetector(BasePatternDetector):
    cycle_length = 0

    def __init__(self, accounts: Dict[str, Any], adjacency_list: Dict[str, Any], network_builder: NetworkBuilder = None):
        super().__init__(accounts, adjacency_list)
        self.network_builder = network_builder
        self.loops_detected: Dict[str, RingDetail] = {}

    def detect(self):
        print("Detecting loops (cycles) using modified Johnson's algorithm...")
        
        self.loop_counter = 0

        # Create a sorted list of nodes to iterate through
        # Sorting helps in deterministic execution and allows skipping nodes < start_node
        nodes = sorted(list(self.accounts.keys()))
        
        for start_node in nodes:
            self.cycle_length = 0
            if "payroll" in self.accounts[start_node].tags or "merchant" in self.accounts[start_node].tags:
                continue    
            else:
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
                        
                        if len(stack) > self.cycle_length :
                            self.cycle_length = len(stack)
                         
                        first_edge_time = stack[1][1] if len(stack) > 1 else datetime.min
                        if len(stack) > 1 and edge_timestamp <= first_edge_time:
                             continue

                        self._record_loop(stack)
                else:
                    
                    next_min_time = min_timestamp
                    if len(stack) == 1:
                        # This is the first edge from start_node.
                        # Subsequent edges must be after this one.
                        next_min_time = edge_timestamp
                    
                    self._circuit(start_node, neighbor, stack, next_min_time)
        
        stack.pop()

    def _record_loop(self, stack: List[Tuple[str, datetime]]):
        # Access the global NetworkBuilder instance to build networks immediately upon loop detection
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
        )
        
        if self.network_builder:
            self.network_builder.built_networks(ring_id, detail) # Build network for this loop immediately
        # self._increase_suspicion(members) # User requirement
        self.increase_suspicion(members)

    def increase_suspicion(self, members: List[str]):
        """
        Increases suspicion score for the found members.
        """
        for member_id in members:
            if member_id in self.accounts:
                self.accounts[member_id].IncSuspiciousScore(80.0)
                if "ringtype:loop" not in self.accounts[member_id].tags:
                    self.accounts[member_id].tags.append("ringtype:loop")
