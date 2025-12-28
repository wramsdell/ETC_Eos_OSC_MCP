# OSC Feedback and Operator Learning Guide

This guide explains how to enable and use the OSC feedback system to learn from operator behavior and console state changes.

## Overview

The ETC Eos MCP Server can receive OSC messages FROM the console, not just send TO it. This bidirectional communication enables:

- **Operator Learning**: Watch what human operators do and learn their techniques
- **Error Detection**: See what commands fail and why
- **State Monitoring**: Track active cues, channel selections, and playback state
- **Behavior Analysis**: Identify patterns, common workflows, and timing

## Quick Start

### 1. Enable OSC TX on Your Eos Console

On your ETC Eos console or ETCnomad:

1. Press `[Setup]`
2. Navigate to: **System → Show Control → OSC**
3. Enable **OSC TX** (Transmit)
4. Set **OSC UDP TX Port** to `3033` (or your preferred port)
5. Set **OSC UDP TX IP Address** to your MCP server's IP address
   - For local ETCnomad: `127.0.0.1`
   - For network console: Your computer's IP address

![Example OSC Settings](https://via.placeholder.com/600x300?text=OSC+Settings+Screenshot)

### 2. Configure the MCP Server

Add these environment variables to your `.env` file:

```bash
# Enable OSC feedback reception
EOS_ENABLE_RX=true

# Port to listen on (must match console's TX port)
EOS_RX_PORT=3033

# Existing connection settings
EOS_HOST=127.0.0.1
EOS_PORT=8000
EOS_USER=1
```

### 3. Start the Server

```bash
cd c:\src\ETC_Eos_OSC_MCP\src
python server.py
```

You should see:
```
INFO - Initializing Eos OSC client: 127.0.0.1:8000 (User 1)
INFO - OSC feedback enabled - listening on port 3033
INFO - OSC receiver enabled on port 3033
INFO - ✓ OSC receiver started
```

## Available Feedback Tools

### 1. `eos_get_feedback_log`

Get recent OSC messages from the console.

**Parameters:**
- `category` (optional): Filter by type - `notify`, `error`, `event`, `user_action`, `selection`, `cue`, `patch`, `playback`, `other`
- `limit` (default: 50): Max number of messages (1-500)

**Example:**
```python
# Get all recent messages
eos_get_feedback_log(limit=100)

# Get only errors
eos_get_feedback_log(category="error", limit=20)

# Get cue changes
eos_get_feedback_log(category="cue", limit=30)
```

**Output:**
```json
{
  "success": true,
  "count": 15,
  "category_filter": "error",
  "messages": [
    {
      "timestamp": 1703456789.123,
      "time": "2024-12-24 14:33:09",
      "category": "error",
      "address": "/eos/out/error",
      "args": ["Unknown command"]
    }
  ]
}
```

### 2. `eos_get_recent_errors`

Quickly see what commands failed recently.

**Example:**
```python
eos_get_recent_errors()
```

**Use Case:** Learn what syntax doesn't work, what the operator tried that failed.

### 3. `eos_get_operator_actions`

See what human operators are doing on the console.

**Parameters:**
- `limit` (default: 50): Max number of actions (1-200)

**Example:**
```python
eos_get_operator_actions(limit=100)
```

**Output:**
```json
{
  "success": true,
  "action_count": 42,
  "actions": [
    {
      "timestamp": 1703456850.456,
      "time": "2024-12-24 14:34:10",
      "address": "/eos/out/user/1/action",
      "action": ["Chan 1 Thru 10 At 75"]
    },
    {
      "timestamp": 1703456852.789,
      "time": "2024-12-24 14:34:12",
      "address": "/eos/out/user/1/action",
      "action": ["Record Cue 5"]
    }
  ]
}
```

**Use Case:** Learn operator workflows and preferred command sequences.

### 4. `eos_get_operator_insights`

Analyze operator behavior for patterns and recommendations.

**Parameters:**
- `time_window_minutes` (default: 60): Look back this many minutes (1-1440)

**Example:**
```python
# Analyze last hour
eos_get_operator_insights(time_window_minutes=60)

# Analyze last 10 minutes
eos_get_operator_insights(time_window_minutes=10)
```

**Output:**
```json
{
  "success": true,
  "insights": {
    "time_window_minutes": 60,
    "total_actions": 125,
    "total_feedback_messages": 287,
    "most_common_actions": [
      {"action": "cue", "count": 45},
      {"action": "channel", "count": 38},
      {"action": "selection", "count": 22}
    ],
    "error_count": 3,
    "recent_errors": [
      {
        "time": "14:35:12",
        "error": "['Invalid cue number']"
      }
    ],
    "feedback_by_category": {
      "cue": 89,
      "selection": 67,
      "notify": 45,
      "error": 3
    },
    "average_seconds_between_actions": 2.3,
    "recommendations": [
      "Operator is working rapidly. They may be using keyboard shortcuts or efficient workflows worth learning.",
      "Operator focused on cue programming. They may have established workflows for building cues efficiently."
    ]
  }
}
```

**Use Case:** Understand operator expertise, identify learning opportunities.

### 5. `eos_clear_feedback_log`

Reset the feedback history to start fresh.

**Example:**
```python
eos_clear_feedback_log()
```

## OSC Messages Received

The server listens for these OSC addresses from Eos:

| Address Pattern | Category | Description |
|----------------|----------|-------------|
| `/eos/out/notify` | `notify` | General notifications from console |
| `/eos/out/error` | `error` | Failed commands and errors |
| `/eos/out/event` | `event` | System events |
| `/eos/out/user/*/action` | `user_action` | Operator actions (most valuable!) |
| `/eos/out/user/*/selection` | `selection` | Channel selection changes |
| `/eos/out/cue/*/*` | `cue` | Cue state changes |
| `/eos/out/patch/*` | `patch` | Patch information |
| `/eos/out/dmx/*` | `dmx` | DMX output levels (not logged - too chatty) |
| `/eos/out/playback/*` | `playback` | Playback state |
| `/eos/out/*` | `other` | Any other messages |

## Learning from Operators

### Workflow Pattern Recognition

Monitor operator actions over time to identify:

1. **Command Sequences**: Common multi-step operations
   ```
   Chan 1 Thru 10 At 75
   Record Cue 5 Label Warm_Wash
   Time 3
   ```

2. **Timing Patterns**: How fast they work, delays between actions
   - Rapid fire = experienced operator, learn their shortcuts
   - Long pauses = complex operations or debugging

3. **Error Patterns**: What syntax they struggle with
   - Learn what NOT to do
   - Understand common misunderstandings

4. **Focus Areas**: What they're working on
   - Lots of cue activity = programming cues
   - Patch changes = fixing rig setup
   - Palette work = building looks

### Example Learning Session

```python
# Start monitoring
print("Monitoring operator for 30 minutes...")

# After 30 minutes
insights = eos_get_operator_insights(time_window_minutes=30)

# Review common actions
print(f"Most common operations: {insights['insights']['most_common_actions']}")

# Check for errors (learning opportunities)
errors = eos_get_recent_errors()
print(f"Operator struggled with: {errors}")

# Get specific action details
actions = eos_get_operator_actions(limit=50)
# Analyze sequences manually or with AI
```

### Teaching Moments

When you see errors, you can:
1. Identify the failed command
2. Understand what they were trying to do
3. Learn the correct syntax
4. Add it to your knowledge base

Example:
```json
{
  "error": "Unknown fixture type 'VL2600'",
  "insight": "Operator tried 'VL2600' but Eos expects 'Varilite_VL2600' or fixture number"
}
```

## Architecture

### Feedback Flow

```
┌─────────────┐         OSC TX          ┌──────────────────┐
│  Eos Console│────────────────────────>│  MCP Server      │
│  (ETCnomad) │   Port 3033 (UDP)       │  (Python)        │
└─────────────┘                          │                  │
                                         │  ┌────────────┐  │
Operator types:                          │  │OSC Receiver│  │
"Chan 1 At 50"                          │  └─────┬──────┘  │
                                         │        │         │
Eos sends back:                          │  ┌─────▼──────┐  │
/eos/out/user/1/action                  │  │  Feedback  │  │
["Chan 1 At 50"]                        │  │    Log     │  │
                                         │  └─────┬──────┘  │
                                         │        │         │
                                         │  ┌─────▼──────┐  │
                                         │  │  Behavior  │  │
                                         │  │  Analyzer  │  │
                                         │  └────────────┘  │
                                         └──────────────────┘
```

### Storage

- Feedback messages stored in memory (last 1000 messages)
- Operator actions tracked separately (last 1000 actions)
- Logs cleared on restart or via `eos_clear_feedback_log()`
- DMX feedback NOT stored (too much data)

## Troubleshooting

### No Feedback Received

**Check:**
1. Is `EOS_ENABLE_RX=true` in your `.env`?
2. Is OSC TX enabled on the console?
3. Does console TX port match your RX port?
4. Is console sending to correct IP address?
5. Is firewall blocking port 3033?

**Test:**
```python
# Send a command
eos_send_command("Chan 1 At 50#")

# Check for feedback
feedback = eos_get_feedback_log(limit=10)
print(f"Received {feedback['count']} messages")
```

### Too Much Noise

If you're getting too many messages:

1. **Filter by category**:
   ```python
   # Only errors and user actions
   eos_get_feedback_log(category="error")
   eos_get_operator_actions()
   ```

2. **Increase time between checks**

3. **Clear logs periodically**:
   ```python
   eos_clear_feedback_log()
   ```

### Keystroke-Level Monitoring

⚠️ **Important**: Eos does NOT send individual keystrokes via OSC. You'll receive:
- Completed commands (via `/eos/out/notify`)
- User actions (via `/eos/out/user/*/action`)
- State changes (cue fires, selection changes, etc.)

You won't see "Chan" then "1" then "At" - you'll see the complete "Chan 1 At 50" command after it's entered.

## Advanced Usage

### Building a Learning Database

```python
import json
from collections import defaultdict

# Collect data over time
patterns = defaultdict(int)

actions = eos_get_operator_actions(limit=200)
for action in actions['actions']:
    cmd = action['action'][0] if action['action'] else ""
    # Extract command type (first word)
    cmd_type = cmd.split()[0] if cmd else ""
    patterns[cmd_type] += 1

# Save for analysis
with open('operator_patterns.json', 'w') as f:
    json.dump(dict(patterns), f, indent=2)
```

### Real-Time Monitoring

```python
import time

print("Starting real-time operator monitor...")
print("Press Ctrl+C to stop\n")

last_count = 0
try:
    while True:
        actions = eos_get_operator_actions(limit=10)
        current_count = actions['action_count']

        if current_count > last_count:
            # New actions!
            new_actions = actions['actions'][last_count:]
            for action in new_actions:
                print(f"[{action['time']}] Operator: {action['action']}")
            last_count = current_count

        time.sleep(2)  # Check every 2 seconds
except KeyboardInterrupt:
    print("\nMonitoring stopped")
```

## Next Steps

1. **Enable feedback** on your setup
2. **Monitor an operator** session to see what data you get
3. **Review insights** to understand patterns
4. **Build knowledge** from errors and successes
5. **Iterate** - adjust what you track based on what's useful

The feedback system turns every operator session into a learning opportunity!