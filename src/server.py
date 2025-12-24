"""
ETC Eos MCP Server

Main server file that initializes the MCP server and registers all tools.
"""

import os
import logging
from mcp.server.fastmcp import FastMCP

# Import EOS client
from eos_client import EosOSCClient

# Import tool registration functions
from tools.patch import register_patch_tools
from tools.cues import register_cue_tools
from tools.effects import register_effect_tools
from tools.palettes import register_palette_tools

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

logger.info(f"Initializing Eos OSC client: {eos_host}:{eos_port} (User {eos_user})")

eos_client = EosOSCClient(
    host=eos_host,
    port=eos_port,
    user_id=eos_user,
    enable_rx=False  # Set to True if you want to receive OSC feedback
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

logger.info(f"ETC Eos MCP Server initialized successfully")
logger.info(f"Connected to Eos console at {eos_host}:{eos_port}")
logger.info(f"Total tools registered: {len(mcp._tools)}")

# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run()
