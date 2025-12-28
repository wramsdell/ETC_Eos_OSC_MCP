"""
ETC Eos MCP Server

Main server file that initializes the MCP server and registers all tools.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path so imports work correctly
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mcp.server.fastmcp import FastMCP

# Import EOS client
from eos_client import EosOSCClient

# Import tool registration functions
from tools.patch import register_patch_tools
from tools.cues import register_cue_tools
from tools.effects import register_effect_tools
from tools.palettes import register_palette_tools
from tools.feedback import register_feedback_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("eos_mcp")

# Initialize Eos OSC client
# Connection details can be configured via environment variables
eos_host = os.getenv("EOS_HOST", "192.168.1.100")
eos_port = int(os.getenv("EOS_PORT", "3032"))
eos_user = int(os.getenv("EOS_USER", "1"))
eos_enable_rx = os.getenv("EOS_ENABLE_RX", "false").lower() in ("true", "1", "yes")
eos_rx_port = int(os.getenv("EOS_RX_PORT", "3033"))

logger.info(f"Initializing Eos OSC client: {eos_host}:{eos_port} (User {eos_user})")
if eos_enable_rx:
    logger.info(f"OSC feedback enabled - listening on port {eos_rx_port}")

eos_client = EosOSCClient(
    host=eos_host,
    port=eos_port,
    user_id=eos_user,
    enable_rx=eos_enable_rx,
    rx_port=eos_rx_port
)

# Register all tool categories
logger.info("Registering MCP tools...")

register_patch_tools(mcp, eos_client)
logger.info("✓ Patch management tools registered")

register_cue_tools(mcp, eos_client)
logger.info("✓ Cue management tools registered")

register_effect_tools(mcp, eos_client)
logger.info("✓ Effect tools registered")

register_palette_tools(mcp, eos_client)
logger.info("✓ Palette tools registered")

register_feedback_tools(mcp, eos_client)
logger.info("✓ Feedback/learning tools registered")

# Start OSC receiver if enabled
if eos_client.enable_rx:
    eos_client.start_receiver()
    logger.info("✓ OSC receiver started")

logger.info(f"ETC Eos MCP Server initialized successfully")
logger.info(f"Connected to Eos console at {eos_host}:{eos_port}")
# Tools successfully registered (19 total: 4 patch, 5 cue, 2 effect, 3 palette, 5 feedback)

# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run()
