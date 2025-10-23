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


def run_server(port=8000):
    """Start HTTP server in background"""
    server = HTTPServer(('', port), DemoHTTPHandler)
    server.serve_forever()


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


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
    print("🌐 Opening browser at http://localhost:8000/visualize.html")
    webbrowser.open('http://localhost:8000/visualize.html')
    time.sleep(2)
    
    print("\n✨ Browser opened! Watch the magic happen...\n")
    
    # ============================================================================
    # Step 1: Create Wallets
    # ============================================================================
    print_section("STEP 1: Creating Wallets")
    
    manager = WalletManager()
    alice = manager.create_wallet("Alice")
    bob = manager.create_wallet("Bob")
    miner = manager.create_wallet("Miner")
    
    update_demo_state(None, manager.wallets, 1, "Creating Wallets",
                     "Created 3 wallets: Alice, Bob, and Miner")
    time.sleep(2)
    
    # ============================================================================
    # Step 2: Create Blockchain
    # ============================================================================
    print_section("STEP 2: Creating Blockchain & Mining Genesis Block")
    
    blockchain = Blockchain(difficulty=4, initial_reward=50_00000000)
    
    print("Blockchain initialized")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"  Initial Block Reward: {blockchain.initial_reward / 100000000} PYC")
    print(f"  Halving Interval: Every {blockchain.halving_interval:,} blocks")
    print(f"  Max Supply: 21,000,000 PYC (just like Bitcoin!)\n")
    
    update_demo_state(blockchain, manager.wallets, 2, "Blockchain Initialized",
                     f"Max supply: 21 million PYC with halving every {blockchain.halving_interval:,} blocks")
    time.sleep(2)
    
    # Mine genesis block
    update_demo_state(blockchain, manager.wallets, 3, "Mining Genesis Block...",
                     "Miner is solving the proof-of-work puzzle (finding nonce)...")
    
    genesis = blockchain.create_genesis_block(miner.address)
    reward = blockchain.get_block_reward(0)
    
    print(f"\nGenesis block mined!")
    print(f"  Miner reward: {reward / 100000000} PYC")
    
    update_demo_state(blockchain, manager.wallets, 4, "Genesis Block Mined!",
                     f"⛏️ Mining Reward: Miner receives {reward / 100000000} PYC")
    
    print("\nBalances after genesis:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 3: Create Transactions
    # ============================================================================
    print_section("STEP 3: Creating Transactions")
    
    print("Transaction 1: Miner -> Alice (20 PYC)")
    update_demo_state(blockchain, manager.wallets, 5, "Creating Transaction",
                     "📤 Miner sends 20 PYC to Alice")
    
    tx1 = miner.send(blockchain, alice.address, 20.0, fee_btc=0.001)
    time.sleep(2)
    
    print("\nTransaction 2: Miner -> Bob (15 PYC)")
    update_demo_state(blockchain, manager.wallets, 6, "Creating Transaction",
                     "📤 Miner sends 15 PYC to Bob")
    
    tx2 = miner.send(blockchain, bob.address, 15.0, fee_btc=0.001)
    
    if not tx1 or not tx2:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    time.sleep(2)
    
    # ============================================================================
    # Step 4: Mine Block 1
    # ============================================================================
    print_section("STEP 4: Mining Block 1")
    
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
                         f"Block confirmed! Miner earned {reward / 100000000} PYC reward")
    
    print("\nBalances after Block 1:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 5: More Transactions
    # ============================================================================
    print_section("STEP 5: More Transactions")
    
    print("Transaction 3: Alice -> Bob (5 PYC)")
    update_demo_state(blockchain, manager.wallets, 9, "Creating Transaction",
                     "📤 Alice sends 5 PYC to Bob")
    
    tx3 = alice.send(blockchain, bob.address, 5.0, fee_btc=0.001)
    time.sleep(2)
    
    print("\nTransaction 4: Bob -> Alice (10 PYC)")
    update_demo_state(blockchain, manager.wallets, 10, "Creating Transaction",
                     "📤 Bob sends 10 PYC back to Alice")
    
    tx4 = bob.send(blockchain, alice.address, 10.0, fee_btc=0.001)
    
    if not tx3 or not tx4:
        print("ERROR: Failed to create transactions")
        sys.exit(1)
    
    print(f"\nPending transactions: {len(blockchain.pending_transactions)}")
    time.sleep(2)
    
    # ============================================================================
    # Step 6: Mine Block 2
    # ============================================================================
    print_section("STEP 6: Mining Block 2")
    
    print("Mining block with pending transactions...")
    update_demo_state(blockchain, manager.wallets, 11, "Mining Block 2...",
                     f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
    
    block2 = blockchain.mine_pending_transactions(miner.address)
    
    if block2:
        print(f"\nBlock 2 mined successfully!")
        print(f"  Hash: {block2.hash}")
        print(f"  Transactions: {len(block2.transactions)}")
    
    print("\nFinal Balances:")
    manager.list_wallets(blockchain)
    time.sleep(2)
    
    # ============================================================================
    # Step 7: Validate Blockchain
    # ============================================================================
    print_section("STEP 7: Validating Blockchain")
    
    print("Running blockchain validation...")
    update_demo_state(blockchain, manager.wallets, 12, "Validating Blockchain...",
                     "Checking all blocks and transactions for integrity")
    time.sleep(1)
    
    is_valid = blockchain.validate_chain()
    
    if is_valid:
        print("✓ Blockchain is VALID!")
        update_demo_state(blockchain, manager.wallets, 13, "✓ Blockchain Validated!",
                         "All blocks and transactions verified successfully")
    else:
        print("✗ Blockchain is INVALID!")
        update_demo_state(blockchain, manager.wallets, 13, "✗ Validation Failed",
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
    
    update_demo_state(blockchain, manager.wallets, 14, "Demo Complete!",
                     f"Alice: {alice.get_balance_btc(blockchain):.2f} PYC | "
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
    print("📊 Check http://localhost:8000/visualize.html")
    print("\nPress Ctrl+C to stop the server and exit\n")
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for watching!")
        sys.exit(0)


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
