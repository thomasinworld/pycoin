#!/usr/bin/env python3
"""
PyCoin Live Demo with Real-time Visualization

Runs the blockchain demo and updates the browser visualization in real-time!
"""

import sys
import json
import time
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

from core.wallet import Wallet, WalletManager
from core.blockchain import Blockchain


# Global state for sharing between threads
live_state = {
    'blockchain': None,
    'wallets': {},
    'current_step': 0,
    'message': '',
    'transaction_narrative': ''
}


class LiveDemoHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves files and blockchain state"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/state':
            # Return current blockchain state
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if live_state['blockchain']:
                response = {
                    'blockchain': live_state['blockchain'].to_dict(),
                    'wallets': {
                        name: {
                            'address': wallet.address,
                            'balance': wallet.get_balance_btc(live_state['blockchain'])
                        }
                        for name, wallet in live_state['wallets'].items()
                    },
                    'current_step': live_state['current_step'],
                    'message': live_state['message'],
                    'transaction_narrative': live_state['transaction_narrative']
                }
            else:
                response = {
                    'blockchain': None,
                    'wallets': {},
                    'current_step': 0,
                    'message': 'Initializing...',
                    'transaction_narrative': ''
                }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            # Serve static files
            super().do_GET()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


def run_server(port=8000):
    """Run the HTTP server"""
    server = HTTPServer(('', port), LiveDemoHandler)
    print(f"🌐 Server running at http://localhost:{port}")
    server.serve_forever()


def update_state(blockchain, wallets, step, message, narrative=''):
    """Update the global state"""
    live_state['blockchain'] = blockchain
    live_state['wallets'] = wallets
    live_state['current_step'] = step
    live_state['message'] = message
    live_state['transaction_narrative'] = narrative
    print(f"\n{'='*80}")
    print(f"STEP {step}: {message}")
    if narrative:
        print(f"📝 {narrative}")
    print(f"{'='*80}\n")


def run_live_demo():
    """Run the demo with live updates"""
    
    # Step 1: Create wallets
    manager = WalletManager()
    alice = manager.create_wallet("Alice")
    bob = manager.create_wallet("Bob")
    miner = manager.create_wallet("Miner")
    
    update_state(None, manager.wallets, 1, "Creating Wallets",
                 "Created 3 wallets: Alice, Bob, and Miner")
    time.sleep(3)
    
    # Step 2: Create blockchain
    blockchain = Blockchain(difficulty=4, initial_reward=50_00000000)
    update_state(blockchain, manager.wallets, 2, "Blockchain Initialized",
                 f"Created blockchain with difficulty {blockchain.difficulty} and 21M PYC cap")
    time.sleep(2)
    
    # Step 3: Mine genesis block
    update_state(blockchain, manager.wallets, 3, "Mining Genesis Block...",
                 "Miner is solving the proof-of-work puzzle...")
    
    genesis = blockchain.create_genesis_block(miner.address)
    reward = blockchain.get_block_reward(0)
    
    update_state(blockchain, manager.wallets, 4, "Genesis Block Mined!",
                 f"Miner received {reward / 100000000} PYC reward")
    time.sleep(3)
    
    # Step 5: Transaction 1 - Miner sends to Alice
    update_state(blockchain, manager.wallets, 5, "Creating Transaction",
                 "Miner sends 20 PYC to Alice")
    
    tx1 = miner.send(blockchain, alice.address, 20.0, fee_btc=0.001)
    time.sleep(2)
    
    # Step 6: Transaction 2 - Miner sends to Bob
    update_state(blockchain, manager.wallets, 6, "Creating Transaction",
                 "Miner sends 15 PYC to Bob")
    
    tx2 = miner.send(blockchain, bob.address, 15.0, fee_btc=0.001)
    time.sleep(2)
    
    # Step 7: Mine block 1
    update_state(blockchain, manager.wallets, 7, "Mining Block 1...",
                 f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
    
    block1 = blockchain.mine_pending_transactions(miner.address)
    reward = blockchain.get_block_reward(1)
    
    update_state(blockchain, manager.wallets, 8, "Block 1 Mined!",
                 f"Block added to chain. Miner earned {reward / 100000000} PYC")
    time.sleep(3)
    
    # Step 9: Transaction 3 - Alice sends to Bob
    update_state(blockchain, manager.wallets, 9, "Creating Transaction",
                 "Alice sends 5 PYC to Bob")
    
    tx3 = alice.send(blockchain, bob.address, 5.0, fee_btc=0.001)
    time.sleep(2)
    
    # Step 10: Transaction 4 - Bob sends to Alice
    update_state(blockchain, manager.wallets, 10, "Creating Transaction",
                 "Bob sends 10 PYC back to Alice")
    
    tx4 = bob.send(blockchain, alice.address, 10.0, fee_btc=0.001)
    time.sleep(2)
    
    # Step 11: Mine block 2
    update_state(blockchain, manager.wallets, 11, "Mining Block 2...",
                 f"Mining block with {len(blockchain.pending_transactions)} pending transactions")
    
    block2 = blockchain.mine_pending_transactions(miner.address)
    
    update_state(blockchain, manager.wallets, 12, "Block 2 Mined!",
                 "Blockchain complete! All transactions confirmed.")
    time.sleep(2)
    
    # Final state
    total_minted = sum(blockchain.get_block_reward(i) for i in range(len(blockchain.chain)))
    total_supply = sum(w.get_balance_btc(blockchain) for w in manager.wallets.values())
    
    update_state(blockchain, manager.wallets, 13, "Demo Complete!",
                 f"Final balances - Alice: {alice.get_balance_btc(blockchain):.8f} PYC, "
                 f"Bob: {bob.get_balance_btc(blockchain):.8f} PYC, "
                 f"Miner: {miner.get_balance_btc(blockchain):.8f} PYC | "
                 f"Total Supply: {total_supply:.2f} / 21,000,000 PYC")
    
    # Validate blockchain
    time.sleep(2)
    is_valid = blockchain.validate_chain()
    update_state(blockchain, manager.wallets, 14, 
                 "✓ Blockchain Validated!" if is_valid else "✗ Validation Failed",
                 f"Blockchain integrity check: {'PASSED' if is_valid else 'FAILED'}")
    
    # Save to file
    blockchain.save_to_file('blockchain.json')
    manager.save_to_file('wallets.json')
    
    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)
    print("✅ Blockchain created and validated")
    print("✅ Files saved: blockchain.json, wallets.json")
    print("✅ Visualization running at http://localhost:8000/live_visualize.html")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🪙  PyCoin Live Demo - Real-time Blockchain Visualization  🪙   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

This demo will:
1. Create a blockchain from scratch
2. Show every step in your browser in real-time
3. Mine blocks with live updates
4. Display transaction narratives

Starting in 3 seconds...
""")
    
    time.sleep(3)
    
    # Start web server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)
    
    # Open browser
    print("🌐 Opening browser...")
    webbrowser.open('http://localhost:8000/live_visualize.html')
    
    time.sleep(2)
    
    # Run the demo
    try:
        run_live_demo()
        
        # Keep server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for watching!")
        sys.exit(0)


if __name__ == "__main__":
    main()

