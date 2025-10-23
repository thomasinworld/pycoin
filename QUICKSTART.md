# 🚀 Quick Start Guide - PyCoin Visualization

## How to Run Locally

### Step 1: Generate Blockchain Data
```bash
cd /Users/thomasrooney/src/pycoin
source venv/bin/activate
python demo.py
```

This creates `blockchain.json` with all the blockchain data.

### Step 2: Open Visualization

**Option A: Double-click** (Easiest)
```
Simply double-click visualize.html in Finder
```

**Option B: Command line**
```bash
# macOS
open visualize.html

# Linux
xdg-open visualize.html

# Windows
start visualize.html
```

**Option C: Drag & Drop**
```
Open visualize.html in any browser
Then drag & drop blockchain.json onto the page
```

---

## 🎬 Animation Controls

The visualizer now has **animated playback** of blockchain creation!

### Controls Available:

| Button | Function |
|--------|----------|
| 🔄 **Replay Animation** | Restart the animation from block 0 |
| ⏸️ **Pause** / ▶️ **Play** | Pause or resume the animation |
| ⏭️ **Skip to End** | Jump to final state (all blocks visible) |
| ⚡ **Speed Slider** | Adjust playback speed (0.5x to 3x) |
| **Progress Bar** | Shows current progress (X / Y blocks) |

### Default Settings:
- **Speed**: 1x (2 seconds per block)
- **Auto-play**: Starts automatically when loaded
- **Mining Animation**: Blocks pulse while "mining"

### Speed Options:
- **0.5x** - Slow motion (4 seconds per block)
- **1.0x** - Normal speed (2 seconds per block)
- **1.5x** - Faster (1.3 seconds per block)
- **2.0x** - Fast (1 second per block)
- **2.5x** - Very fast (0.8 seconds per block)
- **3.0x** - Ultra fast (0.67 seconds per block)

---

## 🎨 What You'll See

### Animated Sequence:
1. **Statistics load** - Shows overview stats
2. **Genesis block appears** - With mining pulse animation
3. **Block slides in** - Smooth fade-in effect
4. **Arrow appears** - Linking to next block
5. **Next block mines** - Repeats for each block
6. **Progress updates** - Real-time progress bar

### Visual Feedback:
- 🔵 **Pulse animation** during "mining"
- ⬇️ **Arrows** connect blocks
- 📊 **Progress bar** fills as animation plays
- 💰 **Transaction details** expand per block

---

## 💡 Tips

### Best Viewing Experience:
1. Use a **wide screen** (1400px+ recommended)
2. **Full-screen mode** for immersive experience
3. Try different **speed settings** to see details

### For Presentations:
1. Run demo.py to generate fresh blockchain
2. Open visualize.html
3. Start with **slow speed (0.5x)** for explanation
4. Use **replay button** to demo multiple times
5. **Skip to end** to show final state quickly

### For Learning:
1. Run at **1x speed** first
2. Watch blocks appear one by one
3. **Pause** to inspect block details
4. **Replay** to see it again
5. Read transaction details in each block

---

## 🔧 Troubleshooting

### Blockchain not loading?
- Make sure `blockchain.json` exists (run `python demo.py`)
- Check browser console for errors (F12)
- Try drag & drop method instead

### Animation not starting?
- Click **Replay** button
- Check if it's paused (click Play)
- Refresh the page

### Slow performance?
- Use **Skip to End** for large blockchains
- Close other browser tabs
- Try a different browser (Chrome recommended)

---

## 🎯 Example Workflow

```bash
# 1. Generate fresh blockchain
python demo.py

# 2. Open visualizer
open visualize.html

# 3. Watch the magic happen! ✨
# - Blocks appear one by one
# - Mining animation shows work being done
# - Transactions reveal value transfer
# - Chain grows before your eyes!
```

---

## 📱 Browser Compatibility

✅ **Recommended**: Chrome, Firefox, Safari (latest)
⚠️ **Limited**: Internet Explorer (no animations)

---

## 🎬 Screenshot Guide

### What the animation looks like:

```
┌─────────────────────────────────────────┐
│  🔄 Replay   ⏸️ Pause   ⏭️ Skip   ⚡1x  │
│  ▓▓▓▓▓░░░░░░░░  2/3 blocks             │
└─────────────────────────────────────────┘

┌─────────── Block #0 (Mining...) ───────┐
│  Pulse animation shows mining           │
└────────────────────────────────────────┘
              ⬇️
┌─────────── Block #1 (Mining...) ───────┐
│  Next block appears                     │
└────────────────────────────────────────┘
              ⬇️
┌─────────── Block #2 ───────────────────┐
│  Final block                            │
└────────────────────────────────────────┘
```

---

Enjoy exploring your blockchain! 🎉

