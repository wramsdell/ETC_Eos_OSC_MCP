# Changelog

All notable changes to the ETC Eos MCP Server project.

## [Unreleased] - 2024-12-27

### Added - OSC Feedback and Operator Learning System

#### New Features
- **Bidirectional OSC Communication**: Server can now receive feedback from Eos consoles
- **Operator Behavior Learning**: Monitor and analyze what human operators do on the console
- **Error Tracking**: Capture and review failed commands to understand what doesn't work
- **Pattern Recognition**: Identify common workflows, timing patterns, and command sequences
- **Behavior Insights**: AI-powered analysis of operator expertise and techniques

#### New MCP Tools (5 tools added)
1. `eos_get_feedback_log` - Query recent OSC messages from console
2. `eos_get_recent_errors` - View failed commands and errors
3. `eos_get_operator_actions` - Monitor operator activities in real-time
4. `eos_get_operator_insights` - Analyze behavior patterns with recommendations
5. `eos_clear_feedback_log` - Reset learning history

#### Enhanced Files
- **src/eos_client.py**:
  - Added comprehensive OSC receiver with category-specific handlers
  - Implemented feedback logging with 1000-message circular buffer
  - Added operator action tracking separate from general feedback
  - New methods: `get_feedback_log()`, `get_operator_actions()`, `get_recent_errors()`, `clear_feedback_log()`, `start_receiver()`
  - Specific handlers for: notify, error, event, user_action, selection, cue, patch, DMX, playback

- **src/server.py**:
  - Added environment variable `EOS_ENABLE_RX` to enable/disable feedback
  - Added environment variable `EOS_RX_PORT` to configure listening port
  - Automatic OSC receiver thread startup when enabled
  - Updated tool count from 14 to 19 tools

- **src/tools/feedback.py** (NEW):
  - Complete feedback and learning tool implementation
  - Behavior analysis algorithms
  - Pattern recognition logic
  - Timing analysis
  - Error correlation

#### New Documentation
- **FEEDBACK_GUIDE.md**: Comprehensive 200+ line guide covering:
  - Quick start setup instructions
  - Console configuration with screenshots
  - All 5 feedback tools with examples
  - OSC message reference table
  - Operator learning strategies
  - Troubleshooting guide
  - Advanced usage patterns
  - Real-time monitoring examples

- **CHANGELOG.md** (this file): Project change tracking

- **Updated README.md**:
  - Added feedback features to feature list
  - Added 5 feedback tools to tools section
  - Enhanced console configuration with TX setup
  - Link to FEEDBACK_GUIDE.md

#### Configuration
- New `.env` variables:
  ```bash
  EOS_ENABLE_RX=true    # Enable OSC feedback reception
  EOS_RX_PORT=3033      # Port to listen for console feedback
  ```

#### Architecture Improvements
- Separate storage for operator actions vs general feedback
- Category-based message filtering
- Timestamp tracking for all feedback messages
- Circular buffer prevents memory growth
- Thread-safe OSC receiver
- DMX feedback excluded from storage (too verbose)

### Technical Details

**OSC Addresses Monitored:**
- `/eos/out/notify` - Notifications
- `/eos/out/error` - Errors and failed commands
- `/eos/out/event` - System events
- `/eos/out/user/*/action` - Operator actions (key for learning!)
- `/eos/out/user/*/selection` - Channel selections
- `/eos/out/cue/*/*` - Cue state changes
- `/eos/out/patch/*` - Patch information
- `/eos/out/dmx/*` - DMX levels (logged but not stored)
- `/eos/out/playback/*` - Playback state
- `/eos/out/*` - Catch-all for other messages

**Learning Capabilities:**
- Command frequency analysis
- Workflow pattern recognition
- Timing pattern detection (rapid vs. slow operators)
- Error pattern identification
- Category-based activity analysis
- Automatic recommendations based on behavior

**Performance:**
- In-memory storage (last 1000 messages + last 1000 operator actions)
- Minimal overhead - only stores structured data
- DMX feedback excluded to prevent log spam
- Background thread for OSC reception doesn't block main operations

### Use Cases Enabled

1. **Learning from Experts**: Watch experienced operators and learn their techniques
2. **Syntax Discovery**: See what commands fail to avoid making same mistakes
3. **Workflow Optimization**: Identify efficient command sequences
4. **Debugging Help**: Track console state changes for troubleshooting
5. **Training**: Analyze behavior to understand operator skill level
6. **Pattern Building**: Build databases of common operations
7. **Real-time Monitoring**: Watch console activity as it happens

### Breaking Changes
None - all feedback features are opt-in via `EOS_ENABLE_RX=true`

### Backward Compatibility
- Default behavior unchanged (feedback disabled by default)
- Existing tools unaffected
- No changes to command syntax or parameters
- Graceful degradation when feedback disabled

### Migration Guide
To enable the new feedback features:

1. Update your `.env` file with:
   ```
   EOS_ENABLE_RX=true
   EOS_RX_PORT=3033
   ```

2. Enable OSC TX on your console (see FEEDBACK_GUIDE.md)

3. Restart the MCP server

4. Start using feedback tools!

No code changes required for existing functionality.

---

## [1.0.0] - 2024-12-24

### Initial Release
- Patch management (4 tools)
- Cue control (5 tools)
- Effects (2 tools)
- Palettes (3 tools)
- OSC communication layer
- Command builder utilities
- Input validation
- Complete documentation