from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.models.account_profile import AccountProfile

class BasePatternDetector(ABC):
    def __init__(self, accounts: Dict[str, AccountProfile], adjacency_list: Dict[str, List[Dict[str, Any]]], reverse_adjacency_list: Dict[str, List[Dict[str, Any]]] = None):
        self.accounts = accounts
        self.adjacency_list = adjacency_list
        self.reverse_adjacency_list = reverse_adjacency_list or {}

    @abstractmethod
    def detect(self):
        pass
