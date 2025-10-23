#!/usr/bin/env python3
"""
PyCoin Demo Script

Demonstrates a complete PyCoin implementation flow:
1. Create wallets with key pairs
2. Mine the genesis block
3. Create and sign transactions
4. Mine new blocks
5. Validate the blockchain
"""

import sys
from core.wallet import Wallet, WalletManager
from core.blockchain import Blockchain


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def main():
    """Run the PyCoin demo."""
    print_section("PYCOIN - CRYPTOCURRENCY IN PYTHON")
    print("Educational cryptocurrency implementation demonstrating core concepts.\n")
    
    # ============================================================================
    # Step 1: Create Wallets
    # ============================================================================
    print_section("STEP 1: Creating Wallets")
    
    manager = WalletManager()
    
    # Create wallets for Alice, Bob, and Miner
    alice = manager.create_wallet("Alice")
    bob = manager.create_wallet("Bob")
    miner = manager.create_wallet("Miner")
    
    print("\nWallet Details:")
    alice.print_info()
    
    # ============================================================================
    # Step 2: Create Blockchain and Mine Genesis Block
    # ============================================================================
    print_section("STEP 2: Creating Blockchain & Mining Genesis Block")
    
    # Create blockchain with difficulty 4 (4 leading zeros)
    # Lower difficulty = faster mining for demo purposes
    blockchain = Blockchain(difficulty=4, block_reward=50_00000000)  # 50 PYC
    
    print("Blockchain initialized")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"  Block Reward: {blockchain.block_reward / 100000000} PYC\n")
    
    # Mine genesis block (reward goes to miner)
    genesis = blockchain.create_genesis_block(miner.address)
    
    print(f"\nGenesis block mined!")
    print(f"  Miner reward: {blockchain.block_reward / 100000000} PYC")
    
    # Show balances
    print("\nBalances after genesis:")
    manager.list_wallets(blockchain)
    
    # ============================================================================
    # Step 3: Create Transactions
    # ============================================================================
    print_section("STEP 3: Creating Transactions")
    
    # Miner sends 20 PYC to Alice
    print("Transaction 1: Miner -> Alice (20 PYC)")
    tx1 = miner.send(blockchain, alice.address, 20.0, fee_btc=0.001)
    
    print("\nTransaction 2: Miner -> Bob (15 PYC)")
    tx2 = miner.send(blockchain, bob.address, 15.0, fee_btc=0.001)
    
    if not tx1 or not tx2:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    
    # ============================================================================
    # Step 4: Mine Block with Transactions
    # ============================================================================
    print_section("STEP 4: Mining Block 1")
    
    print("Mining block with pending transactions...")
    block1 = blockchain.mine_pending_transactions(miner.address)
    
    if block1:
        print(f"\nBlock 1 mined successfully!")
        print(f"  Hash: {block1.hash}")
        print(f"  Transactions: {len(block1.transactions)}")
        print(f"  Miner reward: {blockchain.block_reward / 100000000} PYC")
    
    # Show updated balances
    print("\nBalances after Block 1:")
    manager.list_wallets(blockchain)
    
    # ============================================================================
    # Step 5: More Transactions
    # ============================================================================
    print_section("STEP 5: More Transactions")
    
    # Alice sends 5 PYC to Bob
    print("Transaction 3: Alice -> Bob (5 PYC)")
    tx3 = alice.send(blockchain, bob.address, 5.0, fee_btc=0.001)
    
    # Bob sends 10 PYC to Alice
    print("\nTransaction 4: Bob -> Alice (10 PYC)")
    tx4 = bob.send(blockchain, alice.address, 10.0, fee_btc=0.001)
    
    if not tx3 or not tx4:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    
    # ============================================================================
    # Step 6: Mine Block 2
    # ============================================================================
    print_section("STEP 6: Mining Block 2")
    
    print("Mining block with pending transactions...")
    block2 = blockchain.mine_pending_transactions(miner.address)
    
    if block2:
        print(f"\nBlock 2 mined successfully!")
        print(f"  Hash: {block2.hash}")
        print(f"  Transactions: {len(block2.transactions)}")
    
    # Show final balances
    print("\nFinal Balances:")
    manager.list_wallets(blockchain)
    
    # ============================================================================
    # Step 7: Validate Blockchain
    # ============================================================================
    print_section("STEP 7: Validating Blockchain")
    
    print("Running blockchain validation...")
    is_valid = blockchain.validate_chain()
    
    if is_valid:
        print("✓ Blockchain is VALID!")
    else:
        print("✗ Blockchain is INVALID!")
        sys.exit(1)
    
    # ============================================================================
    # Step 8: Display Complete Blockchain
    # ============================================================================
    print_section("STEP 8: Complete Blockchain")
    
    blockchain.print_chain()
    
    # ============================================================================
    # Step 9: Save Blockchain and Wallets
    # ============================================================================
    print_section("STEP 9: Saving to Files")
    
    blockchain.save_to_file('blockchain.json')
    manager.save_to_file('wallets.json')
    
    print("\nFiles saved:")
    print("  blockchain.json - Complete blockchain data")
    print("  wallets.json - All wallet keys and addresses")
    
    # ============================================================================
    # Summary
    # ============================================================================
    print_section("SUMMARY")
    
    print(f"Blockchain Statistics:")
    print(f"  Total Blocks: {len(blockchain.chain)}")
    print(f"  Total Transactions: {sum(len(b.transactions) for b in blockchain.chain)}")
    print(f"  UTXO Set Size: {len(blockchain.utxo)}")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"\nWallet Balances:")
    
    for name in ["Alice", "Bob", "Miner"]:
        wallet = manager.get_wallet(name)
        balance = wallet.get_balance_btc(blockchain)
        print(f"  {name}: {balance:.8f} PYC")
    
    print(f"\nTotal Supply: {sum(w.get_balance_btc(blockchain) for w in manager.wallets.values()):.8f} PYC")
    print(f"Expected Supply: {len(blockchain.chain) * (blockchain.block_reward / 100000000):.8f} PYC")
    
    print_section("DEMO COMPLETE")
    print("PyCoin successfully demonstrated cryptocurrency core concepts!")
    print("\nKey Concepts Covered:")
    print("  ✓ Public/Private Key Cryptography (ECDSA)")
    print("  ✓ Address Generation")
    print("  ✓ Transaction Creation and Signing")
    print("  ✓ Transaction Verification")
    print("  ✓ Block Structure and Merkle Trees")
    print("  ✓ Proof-of-Work Mining")
    print("  ✓ Blockchain Validation")
    print("  ✓ UTXO Management")
    print("\nFor more information, see README.md\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

