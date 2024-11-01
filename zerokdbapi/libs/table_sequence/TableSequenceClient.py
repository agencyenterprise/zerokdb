from abc import ABC, abstractmethod
from typing import Tuple

class TableSequenceClient(ABC):
    """Abstract base class defining the interface for table sequence operations"""
    
    @abstractmethod
    async def initialize(self, sender: any) -> str:
        """Initialize the table sequences"""
        pass

    @abstractmethod 
    async def create_sequence(self, sender: any, table_name: str, cid: str) -> str:
        """Create a new sequence"""
        pass

    @abstractmethod
    async def update_sequence_cid(self, sender: any, id: int, new_cid: str) -> str:
        """Update the CID of an existing sequence"""
        pass

    @abstractmethod
    async def get_sequence_by_table_name(self, address: str, table_name: str) -> Tuple[int, str, str]:
        """Get a sequence by its table name"""
        pass
