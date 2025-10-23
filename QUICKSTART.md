# 🚀 PyCoin Quick Start - One Command!

## Super Simple!

```bash
cd /Users/thomasrooney/src/pycoin
source venv/bin/activate
python demo.py
```

**That's it!** The browser opens automatically and you see everything happen live! 🎉

---

## What You'll See

### 1. Browser Opens Automatically
- URL: `http://localhost:7777/visualize.html`
- Python-themed interface (blue & yellow)
- Terminal aesthetic (dark, monospace font)
- No manual steps needed!

### 2. Layout (Split Screen)
```
┌─────────────────────────────────────────┐
│ >>> pycoin  | blocks | txns | stats... │ ← Sticky header
├────────────────┬────────────────────────┤
│  LEFT SIDEBAR  │  CENTER: TERMINAL      │
│  (locked 🔒)   │  (newest at top ⬆️)    │
│                │                        │
│  🔄 restart    │  >>> step 15: ...      │
│  💳 wallet     │  >>> step 14: ...      │
│  💸 send       │  [block #2]            │
│  ⛏ mine        │  >>> step 13: ...      │
│                │  [block #1]            │
│                │  ↓ scroll for history  │
└────────────────┴────────────────────────┘
```

### 3. Live Stats (Header)
Updates in real-time:
- **blocks**: 3
- **transactions**: 9
- **reward**: 50.00 pyc
- **minted**: 150.00 pyc
- **difficulty**: 4 zeros
- **remaining**: 20.85m pyc

### 4. Terminal Output (Newest at Top!)
Latest updates always visible:
```
>>> step 15: demo complete!
  final balances → alice: 25.00 pyc | bob: 10.00 pyc | miner: 115.00 pyc

[block #2]
  hash: 0000a1b2c3...
  previous hash: 00004d5e6f...
  merkle root: 7890abcd...
  nonce: 142567
  timestamp: 2025-10-23 14:32:15
  
  transactions:
    coinbase → 1abc...def (miner): 50.00 pyc
    1def...ghi (alice) → 1jkl...mno (bob): 5.00 pyc

>>> step 14: mining block 2...
  miner is mining block with 1 pending transactions

>>> step 13: creating transaction
  📤 alice sends 5 pyc to bob
    from: 1def...ghi (alice)
    to: 1jkl...mno (bob)
```

### 5. Sidebar (Locked During Demo)
Shows `🔒 locked until demo completes` at top.
After demo finishes, unlocks and you can:
- Create new wallets
- Send PYC between wallets
- Mine blocks
- Validate blockchain
- Show wallet balances
- View blockchain info
- **Restart entire demo** (reruns from scratch!)

### 6. Transaction Narratives
Every action is logged clearly:
- **"miner earns 50 pyc mining reward"**
- **"miner sends 20 pyc to alice"**
- **"alice sends 5 pyc to bob"**
- **"blockchain validated ✓"**

---

## Timeline (~20 seconds)

| Time | What's Happening |
|------|------------------|
| 0s | Browser opens with "Initializing..." |
| 2s | 3 wallets created (Alice, Bob, Miner) |
| 4s | Blockchain initialized (21M cap, halving) |
| 6s | Genesis block being mined... |
| 9s | Genesis block appears! Miner gets 50 PYC |
| 11s | Miner sends 20 PYC to Alice |
| 13s | Miner sends 15 PYC to Bob |
| 15s | Block 1 being mined... |
| 17s | Block 1 appears! Transactions confirmed |
| 19s | Alice sends 5 PYC to Bob |
| 21s | Bob sends 10 PYC back to Alice |
| 23s | Block 2 being mined... |
| 25s | Block 2 appears! |
| 27s | Blockchain validated ✓ |
| 28s | Demo complete! 🎉 |

---

## Features You'll See

### ✅ Live Updates
- **Newest items appear at top** (no scrolling to see latest!)
- Blocks appear as they're mined
- Stats update in real-time (blocks, supply, reward)
- Every action logged as a step
- Full hashes displayed (not truncated)

### ✅ Easy to Understand
- **Transaction narratives**: "alice sends 5 pyc to bob"
- **Wallet names with addresses**: "1A2b3C... (alice)"
- **Clear block details**: nonce, timestamp, merkle root
- **Step-by-step progression**: see every action
- No complex technical jargon

### ✅ Interactive Mode (After Demo)
- **Create wallets**: Add new wallets with custom names
- **Send PYC**: Transfer between any wallets
- **Mine blocks**: Process pending transactions
- **Validate chain**: Check blockchain integrity
- **Show balances**: See all wallet balances
- **Blockchain info**: View chain statistics
- **Restart demo**: Full reset and rerun from beginning

### ✅ No Manual Steps
- Browser opens automatically
- Connects to demo automatically
- Updates in real-time automatically
- Interactive sidebar unlocks when ready
- Everything just works!

---

## Understanding What You See

### Mining
When you see "Mining Block..." the demo is:
1. Collecting pending transactions
2. Creating a block
3. Finding a valid nonce (proof-of-work)
4. Adding block to chain

### Transactions
Format: `Sender sends X PYC to Receiver`
- Shows who's sending
- Shows how much
- Shows who's receiving
- Plain English!

### Balances
- Update after each block is mined
- Show in PYC (not guidos)
- 8 decimal places (like Bitcoin)
- Real-time updates

---

## Stopping the Demo

Press `Ctrl+C` in the terminal:
```
^C
👋 Demo stopped. Thanks for watching!
```

The browser shows the final state. Files are saved:
- `blockchain.json` - Complete blockchain
- `wallets.json` - Wallet keys

---

## Troubleshooting

### Browser didn't open?
Manually visit: `http://localhost:7777/visualize.html`

### Port 7777 in use?
Kill it first:
```bash
lsof -ti:7777 | xargs kill
```

### Not updating?
- Check terminal for errors
- Refresh browser (F5)
- Make sure venv is activated

### Want to run again?
**Option 1: Click restart button** (in sidebar, after demo completes)
- Clears everything
- Reruns demo from scratch
- No need to restart Python!

**Option 2: Restart Python**
```bash
python demo.py
```
Fresh blockchain, fresh wallets, fresh demo!

---

## Using Interactive Mode

After the initial demo completes (~30 seconds), the sidebar unlocks!

### Create a New Wallet
1. Type wallet name in "wallet name" field
2. Click "➕ create wallet"
3. Watch it appear in terminal output
4. New wallet available in dropdowns instantly

### Send PYC
1. Select sender from "from wallet" dropdown
2. Select recipient from "to wallet" dropdown
3. Enter amount (e.g., "5")
4. Enter fee (default: 0.001)
5. Click "📤 send pyc"
6. Transaction added to pending transactions

### Mine a Block
1. Select miner from "miner wallet" dropdown
2. Click "⛏ mine block"
3. Watch the mining happen in terminal
4. Block appears at top of terminal
5. Miner earns the block reward!

### Other Actions
- **✓ validate chain**: Checks blockchain integrity
- **👛 show wallets**: Lists all wallets and balances
- **📊 blockchain info**: Shows chain statistics

All actions appear as steps in the terminal output!

---

## Pro Tips

### For Learning
- Watch the terminal output (detailed info)
- See transaction narratives in browser
- Notice how balances change
- Understand UTXO model

### For Presentations
- Full screen the browser
- Transaction narratives are audience-friendly
- Live updates keep attention
- Easy to explain what's happening

### For Development
- Check `blockchain.json` after
- Modify `demo.py` timing (time.sleep values)
- Adjust difficulty for faster/slower mining
- Customize transaction amounts

---

## What Happens Behind the Scenes

```
demo.py starts
    ↓
Starts HTTP server on port 7777 (background thread)
    ↓
Opens browser to visualize.html
    ↓
Runs demo sequence (background thread)
    ├─ Step 1: Initialize blockchain
    ├─ Step 2: Create wallets (alice, bob, miner)
    ├─ Step 3-4: Mine genesis block
    ├─ Step 5-8: Create transactions, mine block 1
    ├─ Step 9-12: More transactions, mine block 2
    ├─ Step 13-14: Validate blockchain
    └─ Step 15: Demo complete!
    ↓
Meanwhile, browser polls /api/demo_state every second
    ├─ Gets: step, message, narrative, blockchain, wallets
    ├─ Displays newest items at top
    ├─ Updates stats in header
    └─ Shows blocks as they're mined
    ↓
Demo completes → sidebar unlocks
    ↓
Interactive mode available
    ├─ User actions call API endpoints:
    ├─ /api/create_wallet
    ├─ /api/send_transaction
    ├─ /api/mine_block
    ├─ /api/validate_chain
    ├─ /api/show_wallets
    └─ /api/blockchain_info
    ↓
Each action creates a new step
    ↓
Browser shows step immediately (reversed order)
    ↓
Click restart → /api/restart
    ├─ Resets all state
    ├─ Reruns demo sequence
    └─ Browser shows fresh demo
```

---

## Example Session

```bash
$ cd /Users/thomasrooney/src/pycoin
$ source venv/bin/activate
$ python demo.py

╔═══════════════════════════════════════════════════════╗
║   🪙  PyCoin Demo - Live Blockchain Visualization 🪙  ║
╚═══════════════════════════════════════════════════════╝

🌐 Opening browser at http://localhost:7777/visualize.html

✨ Browser opened! Watch the magic happen...

✨ Starting demo sequence...

================================================================================
                    STEP 1: Creating Blockchain                    
================================================================================
Blockchain initialized
  Difficulty: 4
  Initial Block Reward: 50.0 PYC
  Halving Interval: Every 210,000 blocks
  Max Supply: 21,000,000 PYC

================================================================================
                     STEP 2: Creating Wallets                        
================================================================================
📝 Created 3 wallets: alice, bob, and miner

================================================================================
                  STEP 3: Mining Genesis Block                        
================================================================================

Genesis block mined!
  Miner reward: 50.0 PYC

... (demo continues through 15 steps) ...

================================================================================
                     STEP 15: Demo Complete!                        
================================================================================

Final Balances:
  alice: 25.00 PYC
  bob: 10.00 PYC
  miner: 115.00 PYC

================================================================================
                         DEMO COMPLETE                        
================================================================================

🎮 Interactive mode is now available in the browser!
   Use the UI controls to create wallets, send transactions, and mine blocks

Press Ctrl+C to stop the server and exit
```

**Browser shows everything happening live!** 🎬
- Newest items at top
- All steps logged in terminal output
- Blocks appear as they're mined
- Stats update in real-time
- Interactive sidebar unlocks when complete

---

## That's It!

One command, everything works, easy to understand!

```bash
python demo.py
```

**What you get:**
- 📺 Beautiful Python-themed interface
- 🔄 Restart button to run demo again
- 🎮 Interactive controls to play with blockchain
- 📊 Live stats that update automatically
- 🧪 Perfect for learning and experimentation

Enjoy watching your blockchain come to life! 🎉
