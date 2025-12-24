# Quick Start Guide

This guide will help you get the ETC Eos MCP Server up and running quickly.

## Prerequisites

- Python 3.8 or higher
- ETC Eos console, ETCnomad, or compatible software
- Network connection between computer and console

## Installation Steps

### 1. Clone and Setup

```bash
# If you haven't already, clone the repository
git clone https://github.com/wramsdell/eos-mcp-server.git
cd eos-mcp-server

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Console Connection

The server needs to know your console's IP address and port. You can configure this in two ways:

**Option A: Environment Variables (Recommended)**
```bash
# Windows (Command Prompt)
set EOS_HOST=192.168.1.100
set EOS_PORT=3032
set EOS_USER=1

# Windows (PowerShell)
$env:EOS_HOST="192.168.1.100"
$env:EOS_PORT="3032"
$env:EOS_USER="1"

# Mac/Linux
export EOS_HOST="192.168.1.100"
export EOS_PORT="3032"
export EOS_USER="1"
```

**Option B: Edit server.py**
Open `src/server.py` and modify these lines:
```python
eos_host = os.getenv("EOS_HOST", "YOUR_CONSOLE_IP")  # Change YOUR_CONSOLE_IP
eos_port = int(os.getenv("EOS_PORT", "3032"))
eos_user = int(os.getenv("EOS_USER", "1"))
```

### 3. Configure Eos Console

On your Eos console/ETCnomad:

1. Press `[Setup]`
2. Navigate to `System > Show Control > OSC`
3. Enable `OSC RX` (OSC Receive)
4. Verify `OSC UDP RX Port` is `3032` (default)
5. Note the console's IP address (shown in `About`)

### 4. Test Connection

Before running the full MCP server, test the connection:

```bash
# Run the tests
python -m pytest tests/ -v

# Or test manually with Python
python
>>> from src.eos_client import EosOSCClient
>>> client = EosOSCClient(host="192.168.1.100", port=3032)
>>> client.send_command("Chan 1 At 50#")
>>> # Check if channel 1 goes to 50% on the console
>>> exit()
```

### 5. Run the MCP Server

```bash
cd src
python server.py
```

You should see output like:
```
2025-12-24 10:30:00 - __main__ - INFO - Initializing Eos OSC client: 192.168.1.100:3032 (User 1)
2025-12-24 10:30:00 - eos_client - INFO - Eos OSC Client initialized: 192.168.1.100:3032 (User 1)
2025-12-24 10:30:00 - __main__ - INFO - Registering MCP tools...
2025-12-24 10:30:00 - __main__ - INFO - ✓ Patch management tools registered
2025-12-24 10:30:00 - __main__ - INFO - ✓ Cue management tools registered
2025-12-24 10:30:00 - __main__ - INFO - ✓ Effect tools registered
2025-12-24 10:30:00 - __main__ - INFO - ✓ Palette tools registered
2025-12-24 10:30:00 - __main__ - INFO - ETC Eos MCP Server initialized successfully
2025-12-24 10:30:00 - __main__ - INFO - Connected to Eos console at 192.168.1.100:3032
```

## Quick Usage Examples

Once the server is running, you can use Claude to control your console:

### Patching
```
User: "Patch channels 1 through 10 as generic dimmers at addresses 1/1 through 1/10"
Claude: [uses eos_patch_fixture tool 10 times]

User: "Set the position for channel 5 to X=2, Y=3, Z=5 meters"
Claude: [uses eos_set_fixture_position tool]
```

### Cues
```
User: "Record a cue with channels 1-10 at 75%, call it 'Warm Wash'"
Claude: [selects channels, sets levels, uses eos_record_cue]

User: "Set cue 10 to have a 3 second fade and 1 second delay"
Claude: [uses eos_set_cue_timing]
```

### Effects
```
User: "Create a sine wave intensity effect on channels 1-6, rate 2, size 50"
Claude: [uses eos_create_effect]
```

### Palettes
```
User: "Record a focus palette pointing at stage center"
Claude: [calculates positions, uses eos_record_palette]
```

## Troubleshooting

### Server won't start
- Check Python version: `python --version` (should be 3.8+)
- Verify dependencies installed: `pip list`
- Check for syntax errors in logs

### Commands not executing on console
- Verify console IP address with `ping <console-ip>`
- Check OSC is enabled on console
- Verify port 3032 is correct
- Try sending a test command manually
- Check firewall settings

### Connection refused
- Ensure console and computer are on same network
- Verify console IP address is correct
- Check that no other application is using port 3032

### Console receives commands but nothing happens
- Verify command syntax in console command line
- Check user ID matches (default is 1)
- Ensure console is not in another mode (Live/Blind)
- Check if command line shows errors

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review available tools and their parameters
- Explore the [examples/](examples/) directory (if available)
- Join the discussion at [ETC Community](https://community.etcconnect.com/)

## Tips for ETCnomad Users

1. **Make sure ETCnomad is running first** before starting the MCP server
2. **Check the About screen** in ETCnomad to verify the IP address
3. **Use localhost or 127.0.0.1** if running MCP server on same computer as ETCnomad
4. **Enable Augment3d** in User Settings if using position tools
5. **Test with simple commands** like "Chan 1 At 50#" before complex operations

## Common First Commands to Try

```python
# Set a channel to 50%
Chan 1 At 50#

# Select a range
Chan 1 Thru 10 At 75#

# Record a cue
Record Cue 1 Label Test#

# Fire a cue
Cue 1 Go#
```

Good luck, and happy programming!
