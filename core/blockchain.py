"""
PyCoin blockchain implementation.
Manages the chain of blocks, validates transactions, and handles mining.
"""

import json
from typing import List, Optional, Dict

from .block import Block, create_genesis_block
from .transaction import Transaction, TransactionOutput, create_coinbase_transaction


class Blockchain:
    """
    PyCoin blockchain managing the chain of blocks.
    """
    
    def __init__(self, difficulty: int = 4, block_reward: int = 50_00000000):
        """
        Initialize blockchain.
        
        Args:
            difficulty: Mining difficulty (number of leading zeros)
            block_reward: Mining reward in guidos (default: 50 PYC)
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.block_reward = block_reward
        self.pending_transactions: List[Transaction] = []
        
        # UTXO (Unspent Transaction Output) set
        # Maps "tx_id:output_index" -> TransactionOutput
        self.utxo: Dict[str, TransactionOutput] = {}
        
        # Track spent outputs
        self.spent_outputs: set = set()
    
    def create_genesis_block(self, miner_address: str) -> Block:
        """
        Create and add genesis block to chain.
        
        Args:
            miner_address: Address to receive genesis reward
            
        Returns:
            Genesis block
        """
        genesis = create_genesis_block(miner_address, self.block_reward, self.difficulty)
        genesis.mine(self.difficulty)
        self.chain.append(genesis)
        
        # Add genesis coinbase output to UTXO set
        coinbase_tx = genesis.transactions[0]
        self._add_utxos(coinbase_tx)
        
        print(f"Genesis block created: {genesis.hash}")
        return genesis
    
    def get_latest_block(self) -> Optional[Block]:
        """
        Get the most recent block in the chain.
        
        Returns:
            Latest block or None if chain is empty
        """
        return self.chain[-1] if self.chain else None
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to pending transactions.
        
        Args:
            transaction: Transaction to add
            
        Returns:
            True if transaction is valid and added, False otherwise
        """
        # Skip validation for coinbase transactions
        if transaction.inputs[0].prev_tx_id == "0" * 64:
            self.pending_transactions.append(transaction)
            return True
        
        # Validate transaction
        if not self._validate_transaction(transaction):
            print(f"Transaction validation failed: {transaction.tx_id}")
            return False
        
        self.pending_transactions.append(transaction)
        print(f"Transaction added to pending pool: {transaction.tx_id[:16]}...")
        return True
    
    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """
        Mine a new block with pending transactions.
        
        Args:
            miner_address: Address to receive mining reward
            
        Returns:
            Newly mined block or None if no genesis block
        """
        latest_block = self.get_latest_block()
        if latest_block is None:
            print("No genesis block. Create genesis block first.")
            return None
        
        # Create coinbase transaction for miner reward
        block_height = len(self.chain)
        coinbase = create_coinbase_transaction(
            miner_address,
            self.block_reward,
            block_height
        )
        
        # Combine coinbase with pending transactions
        transactions = [coinbase] + self.pending_transactions
        
        # Create new block
        new_block = Block(
            index=block_height,
            transactions=transactions,
            previous_hash=latest_block.hash,
            difficulty=self.difficulty
        )
        
        # Mine the block (proof-of-work)
        new_block.mine(self.difficulty)
        
        # Add block to chain
        if self._add_block(new_block):
            # Clear pending transactions
            self.pending_transactions = []
            print(f"Block {new_block.index} added to chain")
            return new_block
        else:
            print("Failed to add block to chain")
            return None
    
    def _add_block(self, block: Block) -> bool:
        """
        Add a validated block to the chain.
        
        Args:
            block: Block to add
            
        Returns:
            True if block is valid and added, False otherwise
        """
        # Validate block
        if not self._validate_block(block):
            return False
        
        # Add to chain
        self.chain.append(block)
        
        # Update UTXO set
        for tx in block.transactions:
            # Remove spent outputs
            if tx.inputs[0].prev_tx_id != "0" * 64:  # Skip coinbase
                for inp in tx.inputs:
                    key = f"{inp.prev_tx_id}:{inp.prev_output_index}"
                    if key in self.utxo:
                        del self.utxo[key]
                    self.spent_outputs.add(key)
            
            # Add new outputs
            self._add_utxos(tx)
        
        return True
    
    def _add_utxos(self, transaction: Transaction) -> None:
        """
        Add transaction outputs to UTXO set.
        
        Args:
            transaction: Transaction with outputs to add
        """
        for i, output in enumerate(transaction.outputs):
            key = f"{transaction.tx_id}:{i}"
            self.utxo[key] = output
    
    def _validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validate a transaction.
        
        Args:
            transaction: Transaction to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if inputs are unspent
        for inp in transaction.inputs:
            key = f"{inp.prev_tx_id}:{inp.prev_output_index}"
            
            if key in self.spent_outputs:
                print(f"Double spend detected: {key}")
                return False
            
            if key not in self.utxo:
                print(f"UTXO not found: {key}")
                return False
        
        # Verify signatures
        if not transaction.verify(self.utxo):
            print("Signature verification failed")
            return False
        
        # Check that inputs >= outputs (fee can be 0 or positive)
        input_value = transaction.get_input_value(self.utxo)
        output_value = transaction.get_output_value()
        
        if input_value < output_value:
            print(f"Insufficient funds: input={input_value}, output={output_value}")
            return False
        
        return True
    
    def _validate_block(self, block: Block) -> bool:
        """
        Validate a block before adding to chain.
        
        Args:
            block: Block to validate
            
        Returns:
            True if valid, False otherwise
        """
        latest_block = self.get_latest_block()
        
        # Check index
        if block.index != len(self.chain):
            print(f"Invalid block index: expected {len(self.chain)}, got {block.index}")
            return False
        
        # Check previous hash
        if block.previous_hash != latest_block.hash:
            print("Invalid previous hash")
            return False
        
        # Check proof-of-work
        if not block.is_valid_proof(self.difficulty):
            print("Invalid proof-of-work")
            return False
        
        # Validate transactions
        if not block.validate_transactions(self.utxo):
            print("Transaction validation failed")
            return False
        
        return True
    
    def validate_chain(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            True if chain is valid, False otherwise
        """
        if not self.chain:
            return True
        
        # Check genesis block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0" * 64:
            print("Invalid genesis block")
            return False
        
        # Check each block
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Check index
            if current.index != i:
                print(f"Invalid index at block {i}")
                return False
            
            # Check previous hash
            if current.previous_hash != previous.hash:
                print(f"Invalid previous hash at block {i}")
                return False
            
            # Check proof-of-work
            if not current.is_valid_proof(self.difficulty):
                print(f"Invalid proof-of-work at block {i}")
                return False
        
        print(f"Blockchain is valid ({len(self.chain)} blocks)")
        return True
    
    def get_balance(self, address: str) -> int:
        """
        Get balance for an address.
        
        Args:
            address: PyCoin address
            
        Returns:
            Balance in guidos
        """
        balance = 0
        for key, output in self.utxo.items():
            if output.recipient_address == address:
                balance += output.amount
        return balance
    
    def get_utxos_for_address(self, address: str) -> List[tuple[str, int, TransactionOutput]]:
        """
        Get all unspent outputs for an address.
        
        Args:
            address: PyCoin address
            
        Returns:
            List of (tx_id, output_index, output) tuples
        """
        utxos = []
        for key, output in self.utxo.items():
            if output.recipient_address == address:
                tx_id, output_index = key.split(':', 1)
                utxos.append((tx_id, int(output_index), output))
        return utxos
    
    def to_dict(self) -> dict:
        """
        Convert blockchain to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'difficulty': self.difficulty,
            'block_reward': self.block_reward,
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions]
        }
    
    def save_to_file(self, filename: str) -> None:
        """
        Save blockchain to JSON file.
        
        Args:
            filename: File path to save to
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Blockchain saved to {filename}")
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Blockchain':
        """
        Load blockchain from JSON file.
        
        Args:
            filename: File path to load from
            
        Returns:
            Blockchain instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        blockchain = cls(
            difficulty=data['difficulty'],
            block_reward=data['block_reward']
        )
        
        # Rebuild chain
        for block_data in data['chain']:
            block = Block.from_dict(block_data)
            blockchain.chain.append(block)
            
            # Rebuild UTXO set
            for tx in block.transactions:
                for i, output in enumerate(tx.outputs):
                    key = f"{tx.tx_id}:{i}"
                    blockchain.utxo[key] = output
        
        # Load pending transactions
        blockchain.pending_transactions = [
            Transaction.from_dict(tx_data)
            for tx_data in data.get('pending_transactions', [])
        ]
        
        print(f"Blockchain loaded from {filename}")
        return blockchain
    
    def print_chain(self) -> None:
        """
        Print blockchain information.
        """
        print(f"\n{'='*80}")
        print(f"BLOCKCHAIN ({len(self.chain)} blocks)")
        print(f"{'='*80}")
        print(f"Difficulty: {self.difficulty}")
        print(f"Block Reward: {self.block_reward / 100000000} PYC")
        print(f"Pending Transactions: {len(self.pending_transactions)}")
        print(f"UTXO Set Size: {len(self.utxo)}")
        print()
        
        for block in self.chain:
            print(f"Block #{block.index}")
            print(f"  Hash: {block.hash}")
            print(f"  Previous: {block.previous_hash}")
            print(f"  Merkle Root: {block.merkle_root}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Transactions: {len(block.transactions)}")
            for i, tx in enumerate(block.transactions):
                print(f"    [{i}] {tx.tx_id[:32]}... "
                      f"({len(tx.inputs)} in, {len(tx.outputs)} out)")
            print()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Blockchain(blocks={len(self.chain)}, difficulty={self.difficulty})"

