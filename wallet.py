"""
PyCoin wallet implementation.
Manages keys, creates transactions, and tracks balance.
"""

import json
from typing import List, Optional

from keys import PrivateKey, PublicKey, generate_address
from transaction import Transaction, TransactionInput, TransactionOutput
from blockchain import Blockchain


class Wallet:
    """
    PyCoin wallet for managing keys and creating transactions.
    """
    
    def __init__(self, private_key: Optional[PrivateKey] = None):
        """
        Initialize wallet.
        
        Args:
            private_key: Private key (generates new if None)
        """
        if private_key is None:
            self.private_key, self.public_key, self.address = generate_address()
        else:
            self.private_key = private_key
            self.public_key = private_key.public_key
            self.address = self.public_key.to_address()
    
    @classmethod
    def from_private_key_hex(cls, hex_string: str) -> 'Wallet':
        """
        Create wallet from private key hex string.
        
        Args:
            hex_string: Private key as hex
            
        Returns:
            Wallet instance
        """
        private_key = PrivateKey.from_hex(hex_string)
        return cls(private_key)
    
    @classmethod
    def from_wif(cls, wif: str) -> 'Wallet':
        """
        Create wallet from WIF private key.
        
        Args:
            wif: WIF encoded private key
            
        Returns:
            Wallet instance
        """
        private_key = PrivateKey.from_wif(wif)
        return cls(private_key)
    
    def get_balance(self, blockchain: Blockchain) -> int:
        """
        Get wallet balance from blockchain.
        
        Args:
            blockchain: Blockchain to query
            
        Returns:
            Balance in guidos
        """
        return blockchain.get_balance(self.address)
    
    def get_balance_btc(self, blockchain: Blockchain) -> float:
        """
        Get wallet balance in PYC.
        
        Args:
            blockchain: Blockchain to query
            
        Returns:
            Balance in PYC
        """
        return self.get_balance(blockchain) / 100000000
    
    def create_transaction(
        self,
        blockchain: Blockchain,
        recipient_address: str,
        amount: int,
        fee: int = 1000  # Default fee: 0.00001 PYC
    ) -> Optional[Transaction]:
        """
        Create and sign a transaction.
        
        Args:
            blockchain: Blockchain to query for UTXOs
            recipient_address: Recipient's address
            amount: Amount to send in guidos
            fee: Transaction fee in guidos
            
        Returns:
            Signed transaction or None if insufficient funds
        """
        # Get UTXOs for this address
        utxos = blockchain.get_utxos_for_address(self.address)
        
        if not utxos:
            print("No UTXOs available")
            return None
        
        # Select UTXOs to cover amount + fee
        selected_utxos = []
        total_input = 0
        required_amount = amount + fee
        
        for tx_id, output_index, output in utxos:
            selected_utxos.append((tx_id, output_index, output))
            total_input += output.amount
            
            if total_input >= required_amount:
                break
        
        # Check if we have enough
        if total_input < required_amount:
            print(f"Insufficient funds: have {total_input}, need {required_amount}")
            return None
        
        # Create inputs
        inputs = []
        for tx_id, output_index, output in selected_utxos:
            inp = TransactionInput(
                prev_tx_id=tx_id,
                prev_output_index=output_index
            )
            inputs.append(inp)
        
        # Create outputs
        outputs = []
        
        # Payment to recipient
        outputs.append(TransactionOutput(
            amount=amount,
            recipient_address=recipient_address
        ))
        
        # Change back to sender
        change = total_input - amount - fee
        if change > 0:
            outputs.append(TransactionOutput(
                amount=change,
                recipient_address=self.address
            ))
        
        # Create transaction
        transaction = Transaction(inputs=inputs, outputs=outputs)
        
        # Sign all inputs
        for i, (tx_id, output_index, prev_output) in enumerate(selected_utxos):
            transaction.sign_input(i, self.private_key, prev_output.pubkey_script)
        
        print(f"Transaction created: {transaction.tx_id[:16]}...")
        print(f"  Inputs: {len(inputs)}, Total: {total_input / 100000000} PYC")
        print(f"  Outputs: {len(outputs)}")
        print(f"    To {recipient_address[:20]}...: {amount / 100000000} PYC")
        if change > 0:
            print(f"    Change to {self.address[:20]}...: {change / 100000000} PYC")
        print(f"  Fee: {fee / 100000000} PYC")
        
        return transaction
    
    def send(
        self,
        blockchain: Blockchain,
        recipient_address: str,
        amount_btc: float,
        fee_btc: float = 0.00001
    ) -> Optional[Transaction]:
        """
        Create and broadcast a transaction (convenience method with PYC amounts).
        
        Args:
            blockchain: Blockchain to use
            recipient_address: Recipient's address
            amount_btc: Amount to send in PYC
            fee_btc: Transaction fee in PYC
            
        Returns:
            Transaction if successful, None otherwise
        """
        amount_guidos = int(amount_btc * 100000000)
        fee_guidos = int(fee_btc * 100000000)
        
        transaction = self.create_transaction(
            blockchain,
            recipient_address,
            amount_guidos,
            fee_guidos
        )
        
        if transaction and blockchain.add_transaction(transaction):
            return transaction
        
        return None
    
    def to_dict(self) -> dict:
        """
        Export wallet data.
        
        Returns:
            Dictionary with wallet information
        """
        return {
            'private_key': self.private_key.to_hex(),
            'public_key': self.public_key.to_hex(),
            'address': self.address,
            'wif': self.private_key.to_wif()
        }
    
    def save_to_file(self, filename: str) -> None:
        """
        Save wallet to JSON file.
        
        Args:
            filename: File path to save to
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Wallet saved to {filename}")
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Wallet':
        """
        Load wallet from JSON file.
        
        Args:
            filename: File path to load from
            
        Returns:
            Wallet instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        private_key = PrivateKey.from_hex(data['private_key'])
        wallet = cls(private_key)
        print(f"Wallet loaded from {filename}")
        return wallet
    
    def print_info(self) -> None:
        """
        Print wallet information.
        """
        print(f"\n{'='*80}")
        print(f"WALLET INFO")
        print(f"{'='*80}")
        print(f"Address: {self.address}")
        print(f"Private Key (hex): {self.private_key.to_hex()}")
        print(f"Private Key (WIF): {self.private_key.to_wif()}")
        print(f"Public Key: {self.public_key.to_hex()}")
        print(f"{'='*80}\n")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Wallet(address={self.address})"


class WalletManager:
    """
    Manage multiple wallets.
    """
    
    def __init__(self):
        """Initialize wallet manager."""
        self.wallets: dict[str, Wallet] = {}
    
    def create_wallet(self, name: str) -> Wallet:
        """
        Create a new wallet.
        
        Args:
            name: Name/label for the wallet
            
        Returns:
            New wallet instance
        """
        wallet = Wallet()
        self.wallets[name] = wallet
        print(f"Created wallet '{name}': {wallet.address}")
        return wallet
    
    def add_wallet(self, name: str, wallet: Wallet) -> None:
        """
        Add existing wallet.
        
        Args:
            name: Name/label for the wallet
            wallet: Wallet instance
        """
        self.wallets[name] = wallet
        print(f"Added wallet '{name}': {wallet.address}")
    
    def get_wallet(self, name: str) -> Optional[Wallet]:
        """
        Get wallet by name.
        
        Args:
            name: Wallet name
            
        Returns:
            Wallet instance or None if not found
        """
        return self.wallets.get(name)
    
    def list_wallets(self, blockchain: Optional[Blockchain] = None) -> None:
        """
        List all wallets with balances.
        
        Args:
            blockchain: Blockchain to query balances (optional)
        """
        print(f"\n{'='*80}")
        print(f"WALLETS ({len(self.wallets)})")
        print(f"{'='*80}")
        
        for name, wallet in self.wallets.items():
            balance_str = ""
            if blockchain:
                balance = wallet.get_balance_btc(blockchain)
                balance_str = f" | Balance: {balance:.8f} PYC"
            
            print(f"{name}: {wallet.address}{balance_str}")
        
        print(f"{'='*80}\n")
    
    def save_to_file(self, filename: str) -> None:
        """
        Save all wallets to JSON file.
        
        Args:
            filename: File path to save to
        """
        data = {
            name: wallet.to_dict()
            for name, wallet in self.wallets.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Wallet manager saved to {filename}")
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'WalletManager':
        """
        Load wallet manager from JSON file.
        
        Args:
            filename: File path to load from
            
        Returns:
            WalletManager instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        manager = cls()
        for name, wallet_data in data.items():
            private_key = PrivateKey.from_hex(wallet_data['private_key'])
            wallet = Wallet(private_key)
            manager.wallets[name] = wallet
        
        print(f"Wallet manager loaded from {filename} ({len(manager.wallets)} wallets)")
        return manager
    
    def __repr__(self) -> str:
        """String representation."""
        return f"WalletManager(wallets={len(self.wallets)})"

