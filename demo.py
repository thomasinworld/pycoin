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
                        'balance': w.get_balance_pyc(DEMO_STATE['blockchain']) if DEMO_STATE['blockchain'] else 0
                    }
                    for name, w in DEMO_STATE['wallets'].items()
                },
                'step': DEMO_STATE['step'],
                'message': DEMO_STATE['message'],
                'narrative': DEMO_STATE['narrative'],
                'completed': DEMO_STATE['completed']
            }
            
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/validate_chain':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            is_valid = DEMO_STATE['blockchain'].validate_chain() if DEMO_STATE['blockchain'] else False
            
            # Add validation as a step
            DEMO_STATE['step'] += 1
            update_demo_state(
                DEMO_STATE['blockchain'],
                DEMO_STATE['wallets'],
                DEMO_STATE['step'],
                "Blockchain Validated",
                f"blockchain is {'VALID ✓' if is_valid else 'INVALID ✗'}"
            )
            
            response = {'valid': is_valid}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/show_wallets':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Build wallet info
            wallet_info = []
            for name, wallet in DEMO_STATE['wallets'].items():
                balance = wallet.get_balance_pyc(DEMO_STATE['blockchain']) if DEMO_STATE['blockchain'] else 0
                wallet_info.append(f"{name}: {balance:.2f} pyc ({wallet.address})")
            
            # Add as a step
            DEMO_STATE['step'] += 1
            update_demo_state(
                DEMO_STATE['blockchain'],
                DEMO_STATE['wallets'],
                DEMO_STATE['step'],
                "Wallets Displayed",
                "\n".join(wallet_info) if wallet_info else "no wallets found"
            )
            
            response = {'wallets': wallet_info}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/blockchain_info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if DEMO_STATE['blockchain']:
                bc = DEMO_STATE['blockchain']
                info = (
                    f"blocks: {len(bc.chain)} | "
                    f"pending transactions: {len(bc.pending_transactions)} | "
                    f"difficulty: {bc.difficulty} zeros | "
                    f"reward: {bc.get_block_reward(len(bc.chain)) / 100000000:.2f} pyc"
                )
            else:
                info = "blockchain not initialized"
            
            # Add as a step
            DEMO_STATE['step'] += 1
            update_demo_state(
                DEMO_STATE['blockchain'],
                DEMO_STATE['wallets'],
                DEMO_STATE['step'],
                "Blockchain Info",
                info
            )
            
            response = {'info': info}
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Invalid request'}).encode())
            return
        
        if self.path == '/api/create_wallet':
            try:
                name = data.get('name', '').strip()
                if not name:
                    raise ValueError("Wallet name is required")
                if name.lower() in [w.lower() for w in DEMO_STATE['wallets'].keys()]:
                    raise ValueError(f"Wallet '{name}' already exists")
                
                wallet = DEMO_STATE['wallets'][name] = Wallet()
                DEMO_STATE['step'] += 1
                update_demo_state(
                    DEMO_STATE['blockchain'],
                    DEMO_STATE['wallets'],
                    DEMO_STATE['step'],
                    f"New Wallet Created: {name}",
                    f"Address: {wallet.address}"
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': True, 'address': wallet.address}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
                
        elif self.path == '/api/send_transaction':
            try:
                sender_name = data.get('from')
                recipient_name = data.get('to')
                amount = float(data.get('amount', 0))
                fee = float(data.get('fee', 0.001))
                
                # Case-insensitive wallet lookup
                sender = None
                recipient = None
                for name, wallet in DEMO_STATE['wallets'].items():
                    if name.lower() == sender_name.lower():
                        sender = wallet
                        sender_name = name  # Use actual name
                    if name.lower() == recipient_name.lower():
                        recipient = wallet
                        recipient_name = name  # Use actual name
                
                if not sender:
                    raise ValueError(f"Sender wallet '{sender_name}' not found")
                if not recipient:
                    raise ValueError(f"Recipient wallet '{recipient_name}' not found")
                
                tx = sender.send(DEMO_STATE['blockchain'], recipient.address, amount, fee_pyc=fee)
                if not tx:
                    raise ValueError("Transaction failed (insufficient funds?)")
                
                DEMO_STATE['step'] += 1
                update_demo_state(
                    DEMO_STATE['blockchain'],
                    DEMO_STATE['wallets'],
                    DEMO_STATE['step'],
                    "New Transaction Created",
                    f"📤 {sender_name} sends {amount} PYC to {recipient_name}\n"
                    f"  From: {sender.address}\n"
                    f"  To: {recipient.address}"
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': True, 'tx_id': tx.tx_id}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
                
        elif self.path == '/api/mine_block':
            try:
                miner_name = data.get('miner')
                
                # Case-insensitive wallet lookup
                miner = None
                for name, wallet in DEMO_STATE['wallets'].items():
                    if name.lower() == miner_name.lower():
                        miner = wallet
                        miner_name = name  # Use actual name
                        break
                
                if not miner:
                    raise ValueError(f"Miner wallet '{miner_name}' not found")
                if not DEMO_STATE['blockchain'].pending_transactions:
                    raise ValueError("No pending transactions to mine")
                block_index = len(DEMO_STATE['blockchain'].chain)
                
                DEMO_STATE['step'] += 1
                update_demo_state(
                    DEMO_STATE['blockchain'],
                    DEMO_STATE['wallets'],
                    DEMO_STATE['step'],
                    f"Mining Block {block_index}...",
                    f"Mining block with {len(DEMO_STATE['blockchain'].pending_transactions)} pending transactions"
                )
                
                block = DEMO_STATE['blockchain'].mine_pending_transactions(miner.address)
                if not block:
                    raise ValueError("Mining failed")
                
                reward = DEMO_STATE['blockchain'].get_block_reward(block.index)
                
                DEMO_STATE['step'] += 1
                update_demo_state(
                    DEMO_STATE['blockchain'],
                    DEMO_STATE['wallets'],
                    DEMO_STATE['step'],
                    f"Block {block.index} Mined!",
                    f"Block confirmed! {miner_name} earned {reward / 100000000} PYC reward\n"
                    f"  Address: {miner.address}"
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'success': True,
                    'block_index': block.index,
                    'reward': reward / 100000000
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/restart':
            try:
                # Reset demo state
                DEMO_STATE['blockchain'] = None
                DEMO_STATE['wallets'] = {}
                DEMO_STATE['step'] = 0
                DEMO_STATE['message'] = ''
                DEMO_STATE['narrative'] = ''
                DEMO_STATE['completed'] = False
                
                # Start demo sequence in background thread
                demo_thread = threading.Thread(target=run_demo_sequence, daemon=True)
                demo_thread.start()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': True, 'message': 'Demo restarted'}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Endpoint not found'}).encode())
    
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


def run_demo_sequence():
    """Run the complete demo sequence. Can be called on start or restart."""
    global DEMO_STATE
    
    print("\n✨ Starting demo sequence...\n")
    
    # ============================================================================
    # Step 1: Create Blockchain
    # ============================================================================
    print_section("STEP 1: Creating Blockchain")
    
    blockchain = Blockchain(difficulty=4, initial_reward=50_00000000)
    DEMO_STATE['blockchain'] = blockchain
    
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
    alice = manager.create_wallet("alice")
    bob = manager.create_wallet("bob")
    miner = manager.create_wallet("miner")
    
    DEMO_STATE['wallets'] = manager.wallets
    
    narrative = (
        f"Created 3 wallets:\n"
        f"\n"
        f"  alice:\n"
        f"    {alice.address}\n"
        f"\n"
        f"  bob:\n"
        f"    {bob.address}\n"
        f"\n"
        f"  miner:\n"
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
    
    tx1 = miner.send(blockchain, alice.address, 20.0, fee_pyc=0.001)
    if tx1:
        print("  Transaction created and added to mempool")
        print(f"  TX ID: {tx1.tx_id}\n")
    time.sleep(2)
    
    print("Transaction 2: Miner -> Bob (15 PYC)")
    update_demo_state(blockchain, manager.wallets, 6, "Creating Transaction",
                     f"📤 Miner sends 15 PYC to Bob\n  From: {miner.address}\n  To: {bob.address}")
    
    tx2 = miner.send(blockchain, bob.address, 15.0, fee_pyc=0.001)
    if tx2:
        print("  Transaction created and added to mempool")
        print(f"  TX ID: {tx2.tx_id}\n")
    time.sleep(2)
    
    print(f"Pending transactions: {len(blockchain.pending_transactions)}")
    
    # ============================================================================
    # Step 5: Mine Block 1
    # ============================================================================
    print_section("STEP 5: Mining Block 1")
    
    update_demo_state(blockchain, manager.wallets, 7, "Mining Block 1...",
                     "Miner is including pending transactions in new block...")
    
    print("Mining block with pending transactions...")
    block1 = blockchain.mine_pending_transactions(miner.address)
    reward = blockchain.get_block_reward(1)
    
    print(f"\nBlock 1 mined!")
    print(f"  Hash: {block1.hash}")
    print(f"  Transactions: {len(block1.transactions)}")
    print(f"  Miner reward: {reward / 100000000} PYC")
    
    update_demo_state(blockchain, manager.wallets, 8, "Block 1 Mined!",
                     f"✅ Transactions confirmed! Miner earned {reward / 100000000} PYC reward\n  Address: {miner.address}")
    
    print("\nBalances after block 1:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 6: More Transactions
    # ============================================================================
    print_section("STEP 6: More Transactions")
    
    print("Transaction 3: Alice -> Bob (5 PYC)")
    update_demo_state(blockchain, manager.wallets, 9, "Creating Transaction",
                     f"📤 Alice sends 5 PYC to Bob\n  From: {alice.address}\n  To: {bob.address}")
    
    tx3 = alice.send(blockchain, bob.address, 5.0, fee_pyc=0.001)
    if tx3:
        print("  Transaction created and added to mempool")
        print(f"  TX ID: {tx3.tx_id}\n")
    time.sleep(2)
    
    # ============================================================================
    # Step 7: Mine Block 2
    # ============================================================================
    print_section("STEP 7: Mining Block 2")
    
    update_demo_state(blockchain, manager.wallets, 10, "Mining Block 2...",
                     "Miner is mining another block...")
    
    print("Mining block with pending transactions...")
    block2 = blockchain.mine_pending_transactions(miner.address)
    reward = blockchain.get_block_reward(2)
    
    print(f"\nBlock 2 mined!")
    print(f"  Hash: {block2.hash}")
    print(f"  Transactions: {len(block2.transactions)}")
    print(f"  Miner reward: {reward / 100000000} PYC")
    
    update_demo_state(blockchain, manager.wallets, 11, "Block 2 Mined!",
                     f"✅ Block confirmed! Miner earned {reward / 100000000} PYC reward\n  Address: {miner.address}")
    
    print("\nBalances after block 2:")
    manager.list_wallets(blockchain)
    time.sleep(3)
    
    # ============================================================================
    # Step 8: Validate Blockchain
    # ============================================================================
    print_section("STEP 8: Validating Blockchain")
    
    update_demo_state(blockchain, manager.wallets, 12, "Validating Chain...",
                     "Checking all blocks, hashes, and transactions...")
    
    is_valid = blockchain.validate_chain()
    print(f"Blockchain valid: {is_valid}")
    
    update_demo_state(blockchain, manager.wallets, 13, "Chain Validated!",
                     f"✓ Blockchain is {'VALID' if is_valid else 'INVALID'}!")
    time.sleep(2)
    
    # ============================================================================
    # Step 9: Display Chain
    # ============================================================================
    print_section("STEP 9: Blockchain Summary")
    
    blockchain.print_chain()
    
    update_demo_state(blockchain, manager.wallets, 14, "Blockchain Summary",
                     f"Total blocks: {len(blockchain.chain)} | Total PYC minted: {sum(blockchain.get_block_reward(i) for i in range(len(blockchain.chain))) / 100000000:.2f}")
    time.sleep(2)
    
    # ============================================================================
    # Final Step
    # ============================================================================
    print_section("STEP 15: Demo Complete!")
    
    update_demo_state(blockchain, manager.wallets, 15, "Demo Complete!",
                     f"Final balances → Alice: {alice.get_balance_pyc(blockchain):.2f} PYC | "
                     f"Bob: {bob.get_balance_pyc(blockchain):.2f} PYC | "
                     f"Miner: {miner.get_balance_pyc(blockchain):.2f} PYC")
    
    print(f"\nFinal Balances:")
    print(f"  Alice: {alice.get_balance_pyc(blockchain):.2f} PYC")
    print(f"  Bob: {bob.get_balance_pyc(blockchain):.2f} PYC")
    print(f"  Miner: {miner.get_balance_pyc(blockchain):.2f} PYC")
    
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
    print("\n🎮 Interactive mode is now available in the browser!")
    print("   Use the UI controls to create wallets, send transactions, and mine blocks\n")


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
                    balance = wallet.get_balance_pyc(blockchain)
                    print(f"  {name}: {balance:.8f} PYC")
                    print(f"    Address: {wallet.address}\n")
                    
            elif command.startswith('create '):
                name = command[7:].strip()
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
                sender_name = input("From wallet: ").strip()
                recipient_name = input("To wallet: ").strip()
                
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
                
                tx = sender.send(blockchain, recipient.address, amount, fee_pyc=fee)
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
                    
                miner_name = input("Miner wallet: ").strip()
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
                total_supply = sum(w.get_balance_pyc(blockchain) for w in manager.wallets.values())
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
    
    # Run the demo sequence
    run_demo_sequence()
    
    # ============================================================================
    # Keep server running for interactive mode
    # ============================================================================
    print("\n✨ Browser visualization is still running!")
    print("📊 Check http://localhost:7777/visualize.html")
    print("\n🎮 Interactive mode is now available in the browser!")
    print("   Use the UI controls to create wallets, send transactions, and mine blocks")
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
