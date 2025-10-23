"""
PyCoin block structure and merkle tree implementation.
"""

import json
import time
from typing import List, Optional

from .crypto import double_sha256, bytes_to_hex
from .transaction import Transaction


def calculate_merkle_root(transactions: List[Transaction]) -> str:
    """
    Calculate merkle root of transactions.
    
    The merkle tree is a binary tree where:
    - Leaves are transaction hashes
    - Each parent is the hash of its two children concatenated
    - If odd number of nodes, the last one is duplicated
    
    Args:
        transactions: List of transactions
        
    Returns:
        Merkle root as hex string
    """
    if not transactions:
        return "0" * 64
    
    # Get transaction IDs as current level
    current_level = [tx.tx_id for tx in transactions]
    
    # Build tree bottom-up
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            # If odd number, duplicate the last hash
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            
            # Concatenate and hash (PyCoin uses little-endian)
            combined = left + right
            parent_hash = double_sha256(combined.encode('utf-8'))
            next_level.append(bytes_to_hex(parent_hash[::-1]))
        
        current_level = next_level
    
    return current_level[0]


class Block:
    """
    PyCoin block containing transactions.
    """
    
    def __init__(
        self,
        index: int,
        transactions: List[Transaction],
        previous_hash: str,
        timestamp: Optional[float] = None,
        nonce: int = 0,
        difficulty: int = 4
    ):
        """
        Initialize block.
        
        Args:
            index: Block height/index in chain
            transactions: List of transactions in block
            previous_hash: Hash of previous block
            timestamp: Block timestamp (auto-generated if None)
            nonce: Proof-of-work nonce
            difficulty: Mining difficulty (number of leading zeros required)
        """
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.nonce = nonce
        self.difficulty = difficulty
        self.merkle_root = calculate_merkle_root(transactions)
        self._hash = None
    
    def calculate_hash(self) -> str:
        """
        Calculate block hash from header data.
        
        Returns:
            Block hash as hex string
        """
        # Block header contains:
        # - Previous block hash
        # - Merkle root
        # - Timestamp
        # - Difficulty
        # - Nonce
        header = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'difficulty': self.difficulty,
            'nonce': self.nonce
        }
        
        header_json = json.dumps(header, sort_keys=True)
        block_hash = double_sha256(header_json.encode('utf-8'))
        return bytes_to_hex(block_hash)
    
    @property
    def hash(self) -> str:
        """
        Get block hash (cached).
        
        Returns:
            Block hash as hex string
        """
        if self._hash is None:
            self._hash = self.calculate_hash()
        return self._hash
    
    def mine(self, difficulty: Optional[int] = None) -> int:
        """
        Mine the block by finding a valid nonce (proof-of-work).
        
        Args:
            difficulty: Number of leading zeros required (uses block difficulty if None)
            
        Returns:
            Number of hash attempts made
        """
        if difficulty is None:
            difficulty = self.difficulty
        
        target = "0" * difficulty
        attempts = 0
        
        print(f"Mining block {self.index} with difficulty {difficulty}...")
        start_time = time.time()
        
        while True:
            self._hash = None  # Invalidate cache
            block_hash = self.calculate_hash()
            attempts += 1
            
            if block_hash.startswith(target):
                elapsed = time.time() - start_time
                hash_rate = attempts / elapsed if elapsed > 0 else 0
                print(f"Block mined! Hash: {block_hash}")
                print(f"Nonce: {self.nonce}, Attempts: {attempts:,}, "
                      f"Time: {elapsed:.2f}s, Hash rate: {hash_rate:.0f} H/s")
                return attempts
            
            self.nonce += 1
            
            # Progress indicator every million attempts
            if attempts % 1000000 == 0:
                elapsed = time.time() - start_time
                hash_rate = attempts / elapsed if elapsed > 0 else 0
                print(f"  Attempt {attempts:,} ({hash_rate:.0f} H/s)...")
    
    def is_valid_proof(self, difficulty: Optional[int] = None) -> bool:
        """
        Verify that block hash meets difficulty target.
        
        Args:
            difficulty: Number of leading zeros required (uses block difficulty if None)
            
        Returns:
            True if valid proof-of-work, False otherwise
        """
        if difficulty is None:
            difficulty = self.difficulty
        
        target = "0" * difficulty
        return self.hash.startswith(target)
    
    def validate_transactions(
        self,
        prev_outputs: dict[str, 'transaction.TransactionOutput']
    ) -> bool:
        """
        Validate all transactions in the block.
        
        Args:
            prev_outputs: Dictionary of previous outputs for validation
            
        Returns:
            True if all transactions are valid, False otherwise
        """
        if not self.transactions:
            return False
        
        # First transaction should be coinbase
        if self.transactions[0].inputs[0].prev_tx_id != "0" * 64:
            print("First transaction is not coinbase")
            return False
        
        # Validate remaining transactions
        for i, tx in enumerate(self.transactions[1:], 1):
            if not tx.verify(prev_outputs):
                print(f"Transaction {i} validation failed")
                return False
        
        # Verify merkle root
        if self.merkle_root != calculate_merkle_root(self.transactions):
            print("Merkle root mismatch")
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """
        Convert block to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'index': self.index,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        """
        Create block from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Block instance
        """
        block = cls(
            index=data['index'],
            transactions=[Transaction.from_dict(tx) for tx in data['transactions']],
            previous_hash=data['previous_hash'],
            timestamp=data.get('timestamp'),
            nonce=data.get('nonce', 0),
            difficulty=data.get('difficulty', 4)
        )
        return block
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Block(index={self.index}, hash={self.hash[:16]}..., "
            f"transactions={len(self.transactions)}, nonce={self.nonce})"
        )


def create_genesis_block(
    miner_address: str,
    reward: int = 50_00000000,  # 50 PYC in guidos
    difficulty: int = 4
) -> Block:
    """
    Create the genesis block (first block in blockchain).
    
    Args:
        miner_address: Address to receive mining reward
        reward: Mining reward in guidos (default: 50 PYC)
        difficulty: Mining difficulty
        
    Returns:
        Genesis block
    """
    from .transaction import create_coinbase_transaction
    
    # Create coinbase transaction
    coinbase = create_coinbase_transaction(miner_address, reward, 0)
    
    # Create genesis block
    genesis = Block(
        index=0,
        transactions=[coinbase],
        previous_hash="0" * 64,
        timestamp=time.time(),
        nonce=0,
        difficulty=difficulty
    )
    
    return genesis

