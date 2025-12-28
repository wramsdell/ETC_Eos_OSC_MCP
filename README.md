# ETC Eos MCP Server

MCP (Model Context Protocol) server for controlling ETC Eos family lighting consoles via OSC (Open Sound Control). This enables conversational control of Eos consoles including patch modification, cue creation, effects programming, and palette management.

## Features

- **Patch Management**: Add, modify, and query fixture patches with Augment3d positioning
- **Cue Control**: Create, update, and manage cues with timing and fade settings
- **Effects Programming**: Build and modify lighting effects
- **Palette Management**: Create and update focus, color, beam, and intensity palettes
- **Blind Programming**: Work on cues without affecting live output
- **OSC Communication**: Real-time bidirectional control via Open Sound Control protocol
- **Operator Learning**: Monitor and learn from operator behavior via OSC feedback
- **Error Detection**: Track failed commands to understand what doesn't work
- **Behavior Analysis**: Identify patterns, workflows, and timing from console activity

## Requirements

- Python 3.8 or higher
- ETC Eos console, ETCnomad, or compatible software
- Network connectivity between the MCP server and console

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/wramsdell/eos-mcp-server.git
cd eos-mcp-server
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure console connection**:
Edit the console IP and port in `src/server.py` or set environment variables:
```bash
export EOS_HOST="192.168.1.100"
export EOS_PORT="3032"
```

## Usage

### Running the Server

Start the MCP server:
```bash
python src/server.py
```

The server will connect to your Eos console via OSC and expose tools for control.

### Available Tools

#### Patch Management
- `eos_patch_fixture` - Patch a channel with fixture type and DMX address
- `eos_unpatch_channel` - Remove a channel from the patch
- `eos_set_fixture_position` - Set Augment3d position (X, Y, Z, orientation)
- `eos_get_patch_info` - Query patch information for a channel

#### Cue Control
- `eos_record_cue` - Record current state to a cue
- `eos_update_cue` - Update existing cue with current selection
- `eos_set_cue_timing` - Set fade, delay, and timing parameters
- `eos_fire_cue` - Execute a specific cue
- `eos_delete_cue` - Remove a cue

#### Effects
- `eos_create_effect` - Build a new effect on channels
- `eos_modify_effect` - Edit effect parameters (rate, size, etc.)
- `eos_apply_effect` - Apply effect to channel selection
- `eos_delete_effect` - Remove an effect

#### Palettes
- `eos_record_palette` - Create palette (focus, color, beam, intensity)
- `eos_update_palette` - Modify existing palette
- `eos_apply_palette` - Apply palette to selection
- `eos_delete_palette` - Remove a palette

#### Feedback & Learning (New!)
- `eos_get_feedback_log` - Get recent OSC messages from console
- `eos_get_recent_errors` - View failed commands and errors
- `eos_get_operator_actions` - Watch what operators are doing
- `eos_get_operator_insights` - Analyze behavior patterns and workflows
- `eos_clear_feedback_log` - Reset learning history

See [FEEDBACK_GUIDE.md](FEEDBACK_GUIDE.md) for detailed usage.

## Console Configuration

### Enable OSC on Eos Console

**For sending commands TO the console:**
1. Open Setup → Show Control → OSC
2. Enable **OSC RX** (receive)
3. Set **OSC UDP RX Port** (default: 3032)
4. Note the console's IP address

**For receiving feedback FROM the console (optional but recommended):**
5. Enable **OSC TX** (transmit)
6. Set **OSC UDP TX Port** (default: 3033)
7. Set **OSC UDP TX IP Address** to your MCP server's IP
   - For local ETCnomad: `127.0.0.1`
   - For network console: Your computer's IP

### Network Setup

Ensure the computer running the MCP server can reach the console:
- Both devices on same network subnet
- Firewall allows UDP port 3032
- Test with ping: `ping <console-ip>`

## Example Conversations

```
User: "Patch channels 1 through 10 as Source Four LED at addresses 1/1 through 1/10"
MCP: [patches 10 fixtures sequentially]

User: "Create a warm front wash cue with channels 1-10 at 75%"
MCP: [selects channels, sets levels, records cue]

User: "Build a slow sine wave intensity effect on channels 1 through 6"
MCP: [creates effect with specified parameters]

User: "Record a focus palette with movers 20-24 pointing at stage center"
MCP: [calculates positions, records focus palette]
```

## Architecture

```
eos-mcp-server/
├── src/
│   ├── server.py              # Main MCP server
│   ├── eos_client.py          # OSC communication layer
│   ├── tools/
│   │   ├── patch.py           # Patch management tools
│   │   ├── cues.py            # Cue control tools
│   │   ├── effects.py         # Effect tools
│   │   ├── palettes.py        # Palette tools
│   │   └── general.py         # General control tools
│   └── utils/
│       ├── command_builder.py # OSC command construction
│       └── validators.py      # Input validation helpers
├── tests/
│   └── test_eos_client.py
├── requirements.txt
└── README.md
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Tools

1. Create tool function in appropriate module (e.g., `src/tools/cues.py`)
2. Use `@mcp.tool()` decorator with proper annotations
3. Define Pydantic input model for validation
4. Implement OSC command generation
5. Add documentation and examples

## Troubleshooting

### Connection Issues
- Verify console IP address and port
- Check network connectivity with `ping`
- Ensure OSC is enabled on console
- Check firewall settings

### Command Not Executing
- Verify command syntax matches Eos version
- Check console command line for errors
- Enable OSC logging on console
- Review MCP server logs

### Augment3d Position Issues
- Verify Augment3d is enabled for your user
- Check coordinate system orientation
- Ensure fixtures are properly patched
- Verify position data format

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Related Projects

- [PyEosStreamdeck](https://github.com/wramsdell/PyEosStreamdeck) - Stream Deck integration for Eos
- [ETC Eos Family](https://www.etcconnect.com/Products/Consoles/Eos-Family/) - Official console documentation

## References

- [MCP Protocol](https://modelcontextprotocol.io/)
- [ETC Eos OSC Documentation](https://www.etcconnect.com/webdocs/Controls/EosFamilyOnlineHelp/)
- [Augment3d Documentation](https://www.etcconnect.com/Support/Tutorials/Expert-Topics/Augment3d.aspx)
- [GDTF/MVR Specifications](https://gdtf-share.com/)

## Support

For issues and questions:
- GitHub Issues: [eos-mcp-server/issues](https://github.com/wramsdell/eos-mcp-server/issues)
- ETC Community: [community.etcconnect.com](https://community.etcconnect.com/)

## Acknowledgments

Built with the Model Context Protocol SDK and python-osc library.
Inspired by the lighting programming community's need for more efficient workflows.
