from datetime import timedelta
from typing import List, Dict, Any
from src.models.transaction import Transaction
from src.models.account_profile import AccountProfile

class GraphBuilder:
    def __init__(self, transactions: Dict[str, Transaction]):
        self.transactions = transactions
        self.accounts: Dict[str, AccountProfile] = {}
        self.adjacency_list: Dict[str, List[Dict[str, Any]]] = {}
        self.reverse_adjacency_list: Dict[str, List[Dict[str, Any]]] = {}

    def build_graph(self):
        print("Building graph and account profiles...")
        for tx_id, tx in self.transactions.items():
            # Update Sender Profile
            if tx.sender_id not in self.accounts:
                self.accounts[tx.sender_id] = AccountProfile(account_id=tx.sender_id)
            self.accounts[tx.sender_id].update(
                amount=tx.amount, 
                is_sender=True, 
                counterparty=tx.receiver_id, 
                timestamp=tx.timestamp
            )

            # Update Receiver Profile
            if tx.receiver_id not in self.accounts:
                self.accounts[tx.receiver_id] = AccountProfile(account_id=tx.receiver_id)
            self.accounts[tx.receiver_id].update(
                amount=tx.amount, 
                is_sender=False, 
                counterparty=tx.sender_id, 
                timestamp=tx.timestamp
            )

            # Build Adjacency List (Directed)
            if tx.sender_id not in self.adjacency_list:
                self.adjacency_list[tx.sender_id] = []
            
            edge_data = {
                "receiver": tx.receiver_id,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "transaction_id": tx_id
            }
            self.adjacency_list[tx.sender_id].append(edge_data)

            # Build Reverse Adjacency List (for Fan-In)
            if tx.receiver_id not in self.reverse_adjacency_list:
                self.reverse_adjacency_list[tx.receiver_id] = []
            
            reverse_edge_data = {
                "sender": tx.sender_id,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "transaction_id": tx_id
            }
            self.reverse_adjacency_list[tx.receiver_id].append(reverse_edge_data)

            if len(self.reverse_adjacency_list[tx.receiver_id]) > 1:
                if (self.reverse_adjacency_list[tx.receiver_id][-1]["timestamp"] - self.reverse_adjacency_list[tx.receiver_id][-2]["timestamp"] > timedelta(minutes=2)):
                    pass

        print(f"Graph built with {len(self.accounts)} nodes.")
        return self.accounts, self.adjacency_list, self.reverse_adjacency_list
