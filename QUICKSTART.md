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
- URL: `http://localhost:8000/visualize.html`
- Opens in your default browser
- No manual steps needed!

### 2. Live Demo Indicator
```
🔴 LIVE DEMO
```
A blinking green dot shows it's running in real-time!

### 3. Current Step Display
Shows what's happening right now:
```
Step 5: Creating Transaction
📝 Miner sends 20 PYC to Alice
```

### 4. Wallet Balances (Live Updates!)
Watch balances change as transactions happen:
```
Alice:  20.00000000 PYC
Bob:    15.00000000 PYC
Miner:  64.99800000 PYC
```

### 5. Blocks Appear As They're Mined
- Genesis block mines → appears
- Transactions created → shown
- New block mines → appears
- Chain grows before your eyes!

### 6. Transaction Narratives
Every transaction tells a story:
- **"⛏️ Mining Reward: 50 PYC to Miner"**
- **"📤 Miner sends 20 PYC to Alice"**
- **"📤 Alice sends 5 PYC to Bob"**
- **"📤 Bob sends 10 PYC back to Alice"**

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
- Blocks appear as they're mined
- Balances update instantly
- Transaction narratives show what's happening
- Step counter shows progress

### ✅ Easy to Understand
- "Alice sends 5 PYC to Bob" (not complex TX data!)
- Watch money move between wallets
- See mining rewards
- Understand the flow

### ✅ No Manual Steps
- Browser opens automatically
- Connects to demo automatically
- Updates in real-time automatically
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
Manually visit: `http://localhost:8000/visualize.html`

### Port 8000 in use?
Kill it first:
```bash
lsof -ti:8000 | xargs kill
```

### Not updating?
- Check terminal for errors
- Refresh browser (F5)
- Make sure venv is activated

### Want to run again?
```bash
python demo.py
```
That's it! Fresh blockchain every time.

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
Starts HTTP server on port 8000
    ↓
Opens browser to visualize.html
    ↓
visualize.html checks /api/demo_state
    ↓
Sees live demo running
    ↓
Shows "LIVE DEMO" indicator
    ↓
Polls /api/demo_state every second
    ↓
Gets: step, message, narrative, blockchain
    ↓
Updates display automatically
    ↓
Demo completes
    ↓
Polling stops
    ↓
Final state shown
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

🌐 Opening browser at http://localhost:8000/visualize.html

✨ Browser opened! Watch the magic happen...

================================================================================
                        STEP 1: Creating Wallets                        
================================================================================
📝 Created 3 wallets: Alice, Bob, and Miner

... (demo continues) ...

Press Ctrl+C to stop
```

Browser shows everything happening live! 🎬

---

## That's It!

One command, everything works, easy to understand!

```bash
python demo.py
```

Enjoy watching your blockchain come to life! 🎉
