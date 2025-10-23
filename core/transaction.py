"""
PyCoin transaction structure and operations.
Handles transaction inputs, outputs, signing, and verification.
"""

import json
import time
from typing import List, Optional
from dataclasses import dataclass, asdict

from .crypto import double_sha256, bytes_to_hex, hex_to_bytes
from .keys import PrivateKey, PublicKey


@dataclass
class TransactionInput:
    """
    Transaction input referencing a previous output.
    """
    # Transaction ID of the output being spent
    prev_tx_id: str
    # Index of the output in the previous transaction
    prev_output_index: int
    # Signature script (scriptSig)
    signature_script: str = ""
    # Sequence number (for lock time, usually 0xffffffff)
    sequence: int = 0xffffffff
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionInput':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TransactionOutput:
    """
    Transaction output sending value to an address.
    """
    # Amount in guidos (1 PYC = 100,000,000 guidos)
    amount: int
    # Recipient's PyCoin address
    recipient_address: str
    # Public key script (scriptPubKey)
    pubkey_script: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionOutput':
        """Create from dictionary."""
        return cls(**data)


class Transaction:
    """
    PyCoin transaction.
    """
    
    def __init__(
        self,
        inputs: List[TransactionInput],
        outputs: List[TransactionOutput],
        lock_time: int = 0,
        version: int = 1,
        timestamp: Optional[float] = None,
        tx_id: Optional[str] = None
    ):
        """
        Initialize transaction.
        
        Args:
            inputs: List of transaction inputs
            outputs: List of transaction outputs
            lock_time: Transaction lock time (usually 0)
            version: Transaction version (usually 1)
            timestamp: Transaction timestamp (auto-generated if None)
            tx_id: Transaction ID (auto-calculated if None)
        """
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.lock_time = lock_time
        self.timestamp = timestamp if timestamp is not None else time.time()
        self._tx_id = tx_id
    
    @property
    def tx_id(self) -> str:
        """
        Get transaction ID (hash of transaction data).
        
        Returns:
            Transaction ID as hex string
        """
        if self._tx_id is None:
            self._tx_id = self.calculate_hash()
        return self._tx_id
    
    def calculate_hash(self) -> str:
        """
        Calculate transaction hash (transaction ID).
        
        Returns:
            Transaction hash as hex string
        """
        # Serialize transaction for hashing (without signatures)
        tx_data = self.serialize_for_signing()
        tx_hash = double_sha256(tx_data)
        # Bitcoin uses reversed byte order for display
        return bytes_to_hex(tx_hash[::-1])
    
    def serialize_for_signing(self) -> str:
        """
        Serialize transaction data for signing/hashing.
        
        Returns:
            JSON string of transaction data
        """
        data = {
            'version': self.version,
            'inputs': [
                {
                    'prev_tx_id': inp.prev_tx_id,
                    'prev_output_index': inp.prev_output_index,
                    'sequence': inp.sequence
                }
                for inp in self.inputs
            ],
            'outputs': [out.to_dict() for out in self.outputs],
            'lock_time': self.lock_time
        }
        return json.dumps(data, sort_keys=True)
    
    def sign_input(
        self,
        input_index: int,
        private_key: PrivateKey,
        prev_pubkey_script: str = ""
    ) -> None:
        """
        Sign a specific input with private key.
        
        Args:
            input_index: Index of input to sign
            private_key: Private key for signing
            prev_pubkey_script: Previous output's pubkey script
        """
        if input_index >= len(self.inputs):
            raise ValueError(f"Input index {input_index} out of range")
        
        # Get message to sign (transaction hash)
        message = self.serialize_for_signing().encode('utf-8')
        message_hash = double_sha256(message)
        
        # Sign the hash
        signature = private_key.sign(message_hash)
        
        # Get public key
        public_key = private_key.public_key
        pubkey_hex = public_key.to_hex(compressed=True)
        
        # Create signature script (simplified - just sig + pubkey)
        sig_hex = bytes_to_hex(signature)
        signature_script = f"{sig_hex}:{pubkey_hex}"
        
        # Update input
        self.inputs[input_index].signature_script = signature_script
        self.inputs[input_index].pubkey_script = prev_pubkey_script
        
        # Invalidate cached tx_id since we modified the transaction
        self._tx_id = None
    
    def verify_input(
        self,
        input_index: int,
        prev_output: TransactionOutput
    ) -> bool:
        """
        Verify signature on a specific input.
        
        Args:
            input_index: Index of input to verify
            prev_output: Previous output being spent
            
        Returns:
            True if signature is valid, False otherwise
        """
        if input_index >= len(self.inputs):
            return False
        
        inp = self.inputs[input_index]
        
        # Parse signature script
        if not inp.signature_script or ':' not in inp.signature_script:
            return False
        
        try:
            sig_hex, pubkey_hex = inp.signature_script.split(':', 1)
            signature = hex_to_bytes(sig_hex)
            
            # Reconstruct public key
            public_key = PublicKey.from_hex(pubkey_hex)
            
            # Verify address matches
            expected_address = prev_output.recipient_address
            actual_address = public_key.to_address(compressed=True)
            
            if expected_address != actual_address:
                return False
            
            # Create a copy without signatures for verification
            temp_tx = Transaction(
                inputs=[
                    TransactionInput(
                        prev_tx_id=i.prev_tx_id,
                        prev_output_index=i.prev_output_index,
                        signature_script="",
                        sequence=i.sequence
                    )
                    for i in self.inputs
                ],
                outputs=self.outputs,
                lock_time=self.lock_time,
                version=self.version
            )
            
            # Get message that was signed
            message = temp_tx.serialize_for_signing().encode('utf-8')
            message_hash = double_sha256(message)
            
            # Verify signature
            return public_key.verify(message_hash, signature)
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def verify(self, prev_outputs: dict[str, TransactionOutput]) -> bool:
        """
        Verify all inputs in the transaction.
        
        Args:
            prev_outputs: Dictionary mapping "tx_id:output_index" to TransactionOutput
            
        Returns:
            True if all inputs are valid, False otherwise
        """
        for i, inp in enumerate(self.inputs):
            key = f"{inp.prev_tx_id}:{inp.prev_output_index}"
            if key not in prev_outputs:
                print(f"Previous output not found: {key}")
                return False
            
            prev_output = prev_outputs[key]
            if not self.verify_input(i, prev_output):
                print(f"Input {i} verification failed")
                return False
        
        return True
    
    def get_input_value(self, prev_outputs: dict[str, TransactionOutput]) -> int:
        """
        Calculate total input value.
        
        Args:
            prev_outputs: Dictionary mapping "tx_id:output_index" to TransactionOutput
            
        Returns:
            Total input value in guidos
        """
        total = 0
        for inp in self.inputs:
            key = f"{inp.prev_tx_id}:{inp.prev_output_index}"
            if key in prev_outputs:
                total += prev_outputs[key].amount
        return total
    
    def get_output_value(self) -> int:
        """
        Calculate total output value.
        
        Returns:
            Total output value in guidos
        """
        return sum(out.amount for out in self.outputs)
    
    def get_fee(self, prev_outputs: dict[str, TransactionOutput]) -> int:
        """
        Calculate transaction fee.
        
        Args:
            prev_outputs: Dictionary mapping "tx_id:output_index" to TransactionOutput
            
        Returns:
            Transaction fee in guidos
        """
        return self.get_input_value(prev_outputs) - self.get_output_value()
    
    def to_dict(self) -> dict:
        """
        Convert transaction to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'tx_id': self.tx_id,
            'version': self.version,
            'timestamp': self.timestamp,
            'inputs': [inp.to_dict() for inp in self.inputs],
            'outputs': [out.to_dict() for out in self.outputs],
            'lock_time': self.lock_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """
        Create transaction from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Transaction instance
        """
        return cls(
            inputs=[TransactionInput.from_dict(inp) for inp in data['inputs']],
            outputs=[TransactionOutput.from_dict(out) for out in data['outputs']],
            lock_time=data.get('lock_time', 0),
            version=data.get('version', 1),
            timestamp=data.get('timestamp'),
            tx_id=data.get('tx_id')
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Transaction(tx_id={self.tx_id[:16]}..., "
            f"inputs={len(self.inputs)}, outputs={len(self.outputs)})"
        )


def create_coinbase_transaction(recipient_address: str, amount: int, block_height: int) -> Transaction:
    """
    Create a coinbase transaction (mining reward).
    
    Args:
        recipient_address: Miner's address
        amount: Mining reward in guidos
        block_height: Height of the block
        
    Returns:
        Coinbase transaction
    """
    # Coinbase input has null previous transaction
    coinbase_input = TransactionInput(
        prev_tx_id="0" * 64,  # Null hash
        prev_output_index=0xffffffff,  # Special value for coinbase
        signature_script=f"coinbase_block_{block_height}",
        sequence=0xffffffff
    )
    
    # Output sends reward to miner
    output = TransactionOutput(
        amount=amount,
        recipient_address=recipient_address
    )
    
    return Transaction(
        inputs=[coinbase_input],
        outputs=[output]
    )

