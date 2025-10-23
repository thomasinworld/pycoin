#!/usr/bin/env python3
"""
PyCoin Demo - Interactive Blockchain Visualization

Just run: python demo.py
Everything happens automatically!
"""

import sys
import json
import time
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from core.wallet import Wallet, WalletManager
from core.blockchain import Blockchain


# Global state for live updates
DEMO_STATE = {
    'blockchain': None,
    'wallets': {},
    'step': 0,
    'message': '',
    'narrative': '',
    'completed': False
}


class DemoHTTPHandler(SimpleHTTPRequestHandler):
    """Serves files and provides blockchain state API"""
    
    def do_GET(self):
        if self.path == '/api/demo_state':
            # Return current demo state as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'blockchain': DEMO_STATE['blockchain'].to_dict() if DEMO_STATE['blockchain'] else None,
                'wallets': {
                    name: {
                        'address': w.address,
                        'balance': w.get_balance_btc(DEMO_STATE['blockchain']) if DEMO_STATE['blockchain'] else 0
                    }
                    for name, w in DEMO_STATE['wallets'].items()
                },
                'step': DEMO_STATE['step'],
                'message': DEMO_STATE['message'],
                'narrative': DEMO_STATE['narrative'],
                'completed': DEMO_STATE['completed']
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def update_demo_state(blockchain, wallets, step, message, narrative=''):
    """Update global state and print to console"""
    DEMO_STATE['blockchain'] = blockchain
    DEMO_STATE['wallets'] = wallets
    DEMO_STATE['step'] = step
    DEMO_STATE['message'] = message
    DEMO_STATE['narrative'] = narrative
    
    print(f"\n{'='*80}")
    print(f"STEP {step}: {message}")
    if narrative:
        print(f"📝 {narrative}")
    print(f"{'='*80}")


def run_server(port=7777):
    """Start HTTP server in background"""
    server = HTTPServer(('', port), DemoHTTPHandler)
    server.serve_forever()


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def interactive_mode(blockchain: Blockchain, manager: WalletManager):
    """Interactive mode for users to play with the blockchain."""
    step_counter = 16
    
    print_section("INTERACTIVE MODE")
    print("Now you can interact with the blockchain!")
    print("Type 'help' to see available commands\n")
    
    while True:
        try:
            command = input("pyc>>> ").strip().lower()
            
            if not command:
                continue
                
            if command == 'help':
                print("\nAvailable Commands:")
                print("  help              - Show this help message")
                print("  wallets           - List all wallets and balances")
                print("  create <name>     - Create a new wallet")
                print("  send              - Send PYC between wallets (interactive)")
                print("  mine              - Mine pending transactions")
                print("  blockchain        - Show blockchain details")
                print("  validate          - Validate blockchain")
                print("  quit / exit       - Exit interactive mode")
                print()
                
            elif command == 'wallets':
                print("\nWallets:")
                for name, wallet in manager.wallets.items():
                    balance = wallet.get_balance_btc(blockchain)
                    print(f"  {name}: {balance:.8f} PYC")
                    print(f"    Address: {wallet.address}\n")
                    
            elif command.startswith('create '):
                name = command[7:].strip().title()
                if not name:
                    print("Error: Please provide a wallet name")
                    continue
                if name.lower() in [w.lower() for w in manager.wallets.keys()]:
                    print(f"Error: Wallet '{name}' already exists")
                    continue
                wallet = manager.create_wallet(name)
                print(f"\n✓ Created wallet '{name}'")
                print(f"  Address: {wallet.address}\n")
                
                step_counter += 1
                update_demo_state(blockchain, manager.wallets, step_counter, 
                                f"New Wallet Created: {name}",
                                f"Address: {wallet.address}")
                
            elif command == 'send':
                print("\n--- Send PYC ---")
                sender_name = input("From wallet: ").strip().title()
                recipient_name = input("To wallet: ").strip().title()
                
                if sender_name not in manager.wallets:
                    print(f"Error: Wallet '{sender_name}' not found")
                    continue
                if recipient_name not in manager.wallets:
                    print(f"Error: Wallet '{recipient_name}' not found")
                    continue
                    
                sender = manager.get_wallet(sender_name)
                recipient = manager.get_wallet(recipient_name)
                
                try:
                    amount = float(input("Amount (PYC): ").strip())
                    fee = float(input("Fee (PYC) [default 0.001]: ").strip() or "0.001")
                except ValueError:
                    print("Error: Invalid amount or fee")
                    continue
                
                tx = sender.send(blockchain, recipient.address, amount, fee_btc=fee)
                if tx:
                    print(f"\n✓ Transaction created!")
                    print(f"  TX ID: {tx.tx_id}\n")
                    
                    step_counter += 1
                    update_demo_state(blockchain, manager.wallets, step_counter,
                                    "New Transaction Created",
                                    f"📤 {sender_name} sends {amount} PYC to {recipient_name}\n"
                                    f"  From: {sender.address}\n"
                                    f"  To: {recipient.address}")
                else:
                    print("Error: Transaction failed (insufficient funds?)\n")
                    
            elif command == 'mine':
                if not blockchain.pending_transactions:
                    print("Error: No pending transactions to mine\n")
                    continue
                    
                miner_name = input("Miner wallet: ").strip().title()
                if miner_name not in manager.wallets:
                    print(f"Error: Wallet '{miner_name}' not found")
                    continue
                    
                miner = manager.get_wallet(miner_name)
                print(f"\n⛏ Mining block with {len(blockchain.pending_transactions)} pending transactions...")
                
                step_counter += 1
                update_demo_state(blockchain, manager.wallets, step_counter,
                                f"Mining Block {len(blockchain.chain)}...",
                                f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
                
                block = blockchain.mine_pending_transactions(miner.address)
                if block:
                    reward = blockchain.get_block_reward(len(blockchain.chain) - 1)
                    print(f"✓ Block {block.index} mined!")
                    print(f"  Hash: {block.hash}")
                    print(f"  Transactions: {len(block.transactions)}")
                    print(f"  Reward: {reward / 100000000} PYC\n")
                    
                    step_counter += 1
                    update_demo_state(blockchain, manager.wallets, step_counter,
                                    f"Block {block.index} Mined!",
                                    f"Block confirmed! {miner_name} earned {reward / 100000000} PYC reward\n"
                                    f"  Address: {miner.address}")
                else:
                    print("Error: Mining failed\n")
                    
            elif command == 'blockchain':
                print(f"\nBlockchain Details:")
                print(f"  Total Blocks: {len(blockchain.chain)}")
                print(f"  Total Transactions: {sum(len(b.transactions) for b in blockchain.chain)}")
                print(f"  Difficulty: {blockchain.difficulty}")
                print(f"  Pending Transactions: {len(blockchain.pending_transactions)}")
                print(f"  UTXO Set Size: {len(blockchain.utxo)}")
                
                total_minted = sum(blockchain.get_block_reward(i) for i in range(len(blockchain.chain)))
                total_supply = sum(w.get_balance_btc(blockchain) for w in manager.wallets.values())
                print(f"  Total Supply: {total_supply:.8f} PYC")
                print(f"  Remaining Until Cap: {(21_000_000 - total_minted / 100000000):,.2f} PYC\n")
                
            elif command == 'validate':
                print("\n⚙️ Validating blockchain...")
                is_valid = blockchain.validate_chain()
                if is_valid:
                    print("✓ Blockchain is VALID!\n")
                else:
                    print("✗ Blockchain is INVALID!\n")
                    
            elif command in ['quit', 'exit']:
                print("\n👋 Exiting interactive mode...")
                break
                
            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interactive mode interrupted.")
            break
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Save and exit
    blockchain.save_to_file('blockchain.json')
    manager.save_to_file('wallets.json')
    print("\nFiles saved. Thanks for playing with PyCoin!")
    print("Press Ctrl+C to stop the server and exit\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for watching!")
        sys.exit(0)


def main():
    """Run the PyCoin demo with live visualization."""
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        🪙  PyCoin Demo - Live Blockchain Visualization  🪙        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Watch your blockchain come to life in the browser!

Starting server and opening visualization...
""")
    
    # Start server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)
    
    # Open browser
    print("🌐 Opening browser at http://localhost:7777/visualize.html")
    webbrowser.open('http://localhost:7777/visualize.html')
    time.sleep(2)
    
    print("\n✨ Browser opened! Watch the magic happen...\n")
    
    # ============================================================================
    # Step 1: Create Blockchain
    # ============================================================================
    print_section("STEP 1: Creating Blockchain")
    
    blockchain = Blockchain(difficulty=4, initial_reward=50_00000000)
    
    print("Blockchain initialized")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"  Initial Block Reward: {blockchain.initial_reward / 100000000} PYC")
    print(f"  Halving Interval: Every {blockchain.halving_interval:,} blocks")
    print(f"  Max Supply: 21,000,000 PYC (just like Bitcoin!)\n")
    
    update_demo_state(blockchain, {}, 1, "Blockchain Initialized",
                     f"Max supply: 21 million PYC with halving every {blockchain.halving_interval:,} blocks")
    time.sleep(2)
    
    # ============================================================================
    # Step 2: Create Wallets
    # ============================================================================
    print_section("STEP 2: Creating Wallets")
    
    manager = WalletManager()
    alice = manager.create_wallet("Alice")
    bob = manager.create_wallet("Bob")
    miner = manager.create_wallet("Miner")
    
    narrative = (
        f"Created 3 wallets:\n"
        f"\n"
        f"  Alice:\n"
        f"    {alice.address}\n"
        f"\n"
        f"  Bob:\n"
        f"    {bob.address}\n"
        f"\n"
        f"  Miner:\n"
        f"    {miner.address}"
    )
    
    update_demo_state(blockchain, manager.wallets, 2, "Creating Wallets", narrative)
    time.sleep(2)
    
    # ============================================================================
    # Step 3: Mine Genesis Block
    # ============================================================================
    print_section("STEP 3: Mining Genesis Block")
    
    update_demo_state(blockchain, manager.wallets, 3, "Mining Genesis Block...",
                     "Miner is solving the proof-of-work puzzle (finding nonce)...")
    
    genesis = blockchain.create_genesis_block(miner.address)
    reward = blockchain.get_block_reward(0)
    
    print(f"\nGenesis block mined!")
    print(f"  Miner reward: {reward / 100000000} PYC")
    
    update_demo_state(blockchain, manager.wallets, 4, "Genesis Block Mined!",
                     f"⛏️ Mining Reward: Miner receives {reward / 100000000} PYC\n  Address: {miner.address}")
    
    print("\nBalances after genesis:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 4: Create Transactions
    # ============================================================================
    print_section("STEP 4: Creating Transactions")
    
    print("Transaction 1: Miner -> Alice (20 PYC)")
    update_demo_state(blockchain, manager.wallets, 5, "Creating Transaction",
                     f"📤 Miner sends 20 PYC to Alice\n  From: {miner.address}\n  To: {alice.address}")
    
    tx1 = miner.send(blockchain, alice.address, 20.0, fee_btc=0.001)
    time.sleep(2)
    
    print("\nTransaction 2: Miner -> Bob (15 PYC)")
    update_demo_state(blockchain, manager.wallets, 6, "Creating Transaction",
                     f"📤 Miner sends 15 PYC to Bob\n  From: {miner.address}\n  To: {bob.address}")
    
    tx2 = miner.send(blockchain, bob.address, 15.0, fee_btc=0.001)
    
    if not tx1 or not tx2:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    time.sleep(2)
    
    # ============================================================================
    # Step 5: Mine Block 1
    # ============================================================================
    print_section("STEP 5: Mining Block 1")
    
    print("Mining block with pending transactions...")
    update_demo_state(blockchain, manager.wallets, 7, "Mining Block 1...",
                     f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
    
    block1 = blockchain.mine_pending_transactions(miner.address)
    
    if block1:
        reward = blockchain.get_block_reward(1)
        print(f"\nBlock 1 mined successfully!")
        print(f"  Hash: {block1.hash}")
        print(f"  Transactions: {len(block1.transactions)}")
        print(f"  Miner reward: {reward / 100000000} PYC")
        
        update_demo_state(blockchain, manager.wallets, 8, "Block 1 Mined!",
                         f"Block confirmed! Miner earned {reward / 100000000} PYC reward\n  Address: {miner.address}")
    
    print("\nBalances after Block 1:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 6: More Transactions
    # ============================================================================
    print_section("STEP 6: More Transactions")
    
    print("Transaction 3: Alice -> Bob (5 PYC)")
    update_demo_state(blockchain, manager.wallets, 9, "Creating Transaction",
                     f"📤 Alice sends 5 PYC to Bob\n  From: {alice.address}\n  To: {bob.address}")
    
    tx3 = alice.send(blockchain, bob.address, 5.0, fee_btc=0.001)
    time.sleep(2)
    
    print("\nTransaction 4: Bob -> Alice (10 PYC)")
    update_demo_state(blockchain, manager.wallets, 10, "Creating Transaction",
                     f"📤 Bob sends 10 PYC back to Alice\n  From: {bob.address}\n  To: {alice.address}")
    
    tx4 = bob.send(blockchain, alice.address, 10.0, fee_btc=0.001)
    
    if not tx3 or not tx4:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    time.sleep(2)
    
    # ============================================================================
    # Step 7: Mine Block 2
    # ============================================================================
    print_section("STEP 7: Mining Block 2")
    
    print("Mining block with pending transactions...")
    update_demo_state(blockchain, manager.wallets, 11, "Mining Block 2...",
                     f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
    
    block2 = blockchain.mine_pending_transactions(miner.address)
    
    if block2:
        reward = blockchain.get_block_reward(2)
        print(f"\nBlock 2 mined successfully!")
        print(f"  Hash: {block2.hash}")
        print(f"  Transactions: {len(block2.transactions)}")
        
        update_demo_state(blockchain, manager.wallets, 12, "Block 2 Mined!",
                         f"Block confirmed! Miner earned {reward / 100000000} PYC reward\n  Address: {miner.address}")
    
    print("\nFinal Balances:")
    manager.list_wallets(blockchain)
    time.sleep(2)
    
    # ============================================================================
    # Step 8: Validate Blockchain
    # ============================================================================
    print_section("STEP 8: Validating Blockchain")
    
    print("Running blockchain validation...")
    update_demo_state(blockchain, manager.wallets, 13, "Validating Blockchain...",
                     "Checking all blocks and transactions for integrity")
    time.sleep(1)
    
    is_valid = blockchain.validate_chain()
    
    if is_valid:
        print("✓ Blockchain is VALID!")
        update_demo_state(blockchain, manager.wallets, 14, "✓ Blockchain Validated!",
                         "All blocks and transactions verified successfully")
    else:
        print("✗ Blockchain is INVALID!")
        update_demo_state(blockchain, manager.wallets, 14, "✗ Validation Failed",
                         "Blockchain integrity check failed")
        sys.exit(1)
    
    time.sleep(2)
    
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
    
    total_minted = sum(blockchain.get_block_reward(i) for i in range(len(blockchain.chain)))
    print(f"\nTotal Supply: {sum(w.get_balance_btc(blockchain) for w in manager.wallets.values()):.8f} PYC")
    print(f"Expected Supply: {total_minted / 100000000:.8f} PYC")
    print(f"Remaining Until Cap: {(21_000_000 - total_minted / 100000000):,.2f} PYC")
    
    update_demo_state(blockchain, manager.wallets, 15, "Demo Complete!",
                     f"Final balances → Alice: {alice.get_balance_btc(blockchain):.2f} PYC | "
                     f"Bob: {bob.get_balance_btc(blockchain):.2f} PYC | "
                     f"Miner: {miner.get_balance_btc(blockchain):.2f} PYC")
    
    # Save files
    blockchain.save_to_file('blockchain.json')
    manager.save_to_file('wallets.json')
    
    print("\nFiles saved:")
    print("  blockchain.json - Complete blockchain data")
    print("  wallets.json - All wallet keys and addresses")
    
    DEMO_STATE['completed'] = True
    
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
    print("\nFor more information, see README.md")
    print("\n✨ Browser visualization is still running!")
    print("📊 Check http://localhost:7777/visualize.html")
    
    # Interactive mode
    interactive_mode(blockchain, manager)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
