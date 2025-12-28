"""
ETC Eos OSC Client

Handles OSC communication with ETC Eos family consoles.
Provides methods for sending commands and receiving responses.
"""

import os
from typing import Optional, Dict, Any, List, Tuple
from pythonosc import udp_client, osc_server, dispatcher
import asyncio
import logging

logger = logging.getLogger(__name__)


class EosOSCClient:
    """
    Client for OSC communication with ETC Eos consoles.
    
    This class handles sending OSC messages to control lighting consoles
    and can optionally receive feedback from the console.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        user_id: int = 1,
        enable_rx: bool = False,
        rx_port: int = 3033
    ):
        """
        Initialize Eos OSC client.
        
        Args:
            host: Console IP address (default from EOS_HOST env var or "192.168.1.100")
            port: Console OSC port (default from EOS_PORT env var or 3032)
            user_id: Eos user ID for commands (default: 1)
            enable_rx: Enable receiving OSC from console (default: False)
            rx_port: Port to receive OSC messages on (default: 3033)
        """
        self.host = host or os.getenv("EOS_HOST", "192.168.1.100")
        self.port = int(port or os.getenv("EOS_PORT", 3032))
        self.user_id = user_id
        self.enable_rx = enable_rx
        self.rx_port = rx_port
        
        # Create OSC client for sending
        self.client = udp_client.SimpleUDPClient(self.host, self.port)
        
        # Optional: Setup receiver for feedback
        self.server = None
        self.dispatcher = None
        if enable_rx:
            self._setup_receiver()
        
        logger.info(f"Eos OSC Client initialized: {self.host}:{self.port} (User {self.user_id})")
    
    def _setup_receiver(self):
        """Setup OSC server to receive messages from console."""
        self.dispatcher = dispatcher.Dispatcher()

        # Map specific Eos output patterns for detailed feedback
        self.dispatcher.map("/eos/out/notify", self._handle_notify)
        self.dispatcher.map("/eos/out/error", self._handle_error)
        self.dispatcher.map("/eos/out/event", self._handle_event)
        self.dispatcher.map("/eos/out/user/*/action", self._handle_user_action)
        self.dispatcher.map("/eos/out/user/*/selection", self._handle_selection)
        self.dispatcher.map("/eos/out/cue/*/*", self._handle_cue_feedback)
        self.dispatcher.map("/eos/out/patch/*", self._handle_patch_feedback)
        self.dispatcher.map("/eos/out/dmx/*", self._handle_dmx_feedback)
        self.dispatcher.map("/eos/out/playback/*", self._handle_playback_feedback)

        # Catch-all for any unmapped messages
        self.dispatcher.map("/eos/out/*", self._handle_eos_output)

        # Storage for feedback data
        self.feedback_log = []
        self.operator_actions = []
        self.max_log_size = 1000  # Keep last 1000 messages

        self.server = osc_server.ThreadingOSCUDPServer(
            ("0.0.0.0", self.rx_port),
            self.dispatcher
        )
        logger.info(f"OSC receiver enabled on port {self.rx_port}")

    def _log_feedback(self, category: str, address: str, args: tuple):
        """Log feedback message with timestamp."""
        import time
        entry = {
            'timestamp': time.time(),
            'category': category,
            'address': address,
            'args': args
        }
        self.feedback_log.append(entry)

        # Trim log if too large
        if len(self.feedback_log) > self.max_log_size:
            self.feedback_log = self.feedback_log[-self.max_log_size:]

    def _handle_notify(self, address: str, *args):
        """Handle notification messages from Eos."""
        logger.info(f"Eos Notify: {args}")
        self._log_feedback('notify', address, args)

    def _handle_error(self, address: str, *args):
        """Handle error messages from Eos - important for learning what doesn't work."""
        logger.warning(f"Eos Error: {args}")
        self._log_feedback('error', address, args)

    def _handle_event(self, address: str, *args):
        """Handle system event messages from Eos."""
        logger.info(f"Eos Event: {args}")
        self._log_feedback('event', address, args)

    def _handle_user_action(self, address: str, *args):
        """Handle user action messages - tracks what operators do."""
        logger.info(f"User Action: {address} = {args}")
        self._log_feedback('user_action', address, args)

        # Store operator actions separately for behavior learning
        import time
        self.operator_actions.append({
            'timestamp': time.time(),
            'address': address,
            'action': args
        })

        # Trim operator actions log
        if len(self.operator_actions) > self.max_log_size:
            self.operator_actions = self.operator_actions[-self.max_log_size:]

    def _handle_selection(self, address: str, *args):
        """Handle channel selection changes."""
        logger.debug(f"Selection Changed: {args}")
        self._log_feedback('selection', address, args)

    def _handle_cue_feedback(self, address: str, *args):
        """Handle cue state feedback."""
        logger.debug(f"Cue Feedback: {address} = {args}")
        self._log_feedback('cue', address, args)

    def _handle_patch_feedback(self, address: str, *args):
        """Handle patch information feedback."""
        logger.debug(f"Patch Feedback: {address} = {args}")
        self._log_feedback('patch', address, args)

    def _handle_dmx_feedback(self, address: str, *args):
        """Handle DMX level feedback."""
        # DMX feedback is very chatty, so only log at trace level
        logger.log(5, f"DMX: {address} = {args}")  # TRACE level
        # Don't log DMX to main feedback log - too much data

    def _handle_playback_feedback(self, address: str, *args):
        """Handle playback state feedback."""
        logger.info(f"Playback: {address} = {args}")
        self._log_feedback('playback', address, args)

    def _handle_eos_output(self, address: str, *args):
        """Handle incoming OSC messages from Eos (catch-all)."""
        logger.debug(f"Received OSC: {address} {args}")
        self._log_feedback('other', address, args)
    
    def send_command(self, command_string: str) -> None:
        """
        Send a command line string to Eos.
        
        Args:
            command_string: Eos command line syntax (e.g., "Chan 1 At 50#")
        """
        osc_address = f"/eos/user/{self.user_id}/newcmd"
        self.client.send_message(osc_address, command_string)
        logger.debug(f"Sent command: {command_string}")
    
    def send_key(self, key_name: str) -> None:
        """
        Send a hardkey press to Eos.
        
        Args:
            key_name: Name of key to press (e.g., "go", "back", "update")
        """
        osc_address = f"/eos/user/{self.user_id}/key/{key_name}"
        self.client.send_message(osc_address, 1.0)
        logger.debug(f"Sent key: {key_name}")
    
    def set_channel_level(self, channel: int, level: float) -> None:
        """
        Set channel intensity directly via OSC (bypasses command line).
        
        Args:
            channel: Channel number
            level: Intensity level (0.0 to 100.0)
        """
        osc_address = f"/eos/user/{self.user_id}/chan/{channel}"
        self.client.send_message(osc_address, level)
        logger.debug(f"Set channel {channel} to {level}%")
    
    def fire_cue(self, cue_number: float, cue_list: int = 1) -> None:
        """
        Fire a specific cue.
        
        Args:
            cue_number: Cue number to fire (e.g., 1.5)
            cue_list: Cue list number (default: 1)
        """
        osc_address = f"/eos/user/{self.user_id}/cue/{cue_list}/{cue_number}/fire"
        self.client.send_message(osc_address, 1.0)
        logger.debug(f"Fired cue {cue_number} in list {cue_list}")
    
    def execute_macro(self, macro_number: int) -> None:
        """
        Execute a console macro.
        
        Args:
            macro_number: Macro number to execute
        """
        osc_address = f"/eos/user/{self.user_id}/macro/{macro_number}/fire"
        self.client.send_message(osc_address, 1.0)
        logger.debug(f"Executed macro {macro_number}")
    
    def set_patch_position(
        self,
        channel: int,
        x: float,
        y: float,
        z: float,
        pan: float = 0.0,
        tilt: float = 0.0,
        roll: float = 0.0
    ) -> None:
        """
        Set Augment3d position for a fixture.
        
        Args:
            channel: Channel number
            x: X coordinate in meters
            y: Y coordinate in meters
            z: Z coordinate in meters (height)
            pan: Pan orientation in degrees (default: 0.0)
            tilt: Tilt orientation in degrees (default: 0.0)
            roll: Roll orientation in degrees (default: 0.0)
        """
        osc_address = f"/eos/set/patch/{channel}/augment3d/position"
        self.client.send_message(osc_address, [x, y, z, pan, tilt, roll])
        logger.debug(f"Set channel {channel} position: ({x}, {y}, {z}) orientation: ({pan}, {tilt}, {roll})")
    
    def get_patch_position(self, channel: int) -> None:
        """
        Request Augment3d position for a fixture.
        Note: Requires OSC RX to be enabled to receive the response.
        
        Args:
            channel: Channel number to query
        """
        osc_address = f"/eos/get/patch/{channel}/augment3d/position"
        self.client.send_message(osc_address, [])
        logger.debug(f"Requested position for channel {channel}")
    
    def select_channels(self, start: int, end: Optional[int] = None) -> None:
        """
        Select channels without terminating command line.
        
        Args:
            start: Starting channel number
            end: Ending channel number for range (optional)
        """
        if end is None:
            command = f"Chan {start}"
        else:
            command = f"Chan {start} Thru {end}"
        
        # Don't terminate with # to leave command line open
        osc_address = f"/eos/user/{self.user_id}/newcmd"
        self.client.send_message(osc_address, command)
        logger.debug(f"Selected channels: {command}")
    
    def clear_command_line(self) -> None:
        """Clear the command line."""
        self.send_key("clear")
    
    def switch_user(self, new_user_id: int) -> None:
        """
        Switch to a different user ID for subsequent commands.
        Useful for multi-user workflows or separating OSC from manual control.
        
        Args:
            new_user_id: User ID to switch to (1-999)
        """
        self.user_id = new_user_id
        logger.info(f"Switched to user {new_user_id}")
    
    def ping(self) -> None:
        """Send a ping to verify connection."""
        osc_address = "/eos/ping"
        self.client.send_message(osc_address, "ping")
        logger.debug("Sent ping")
    
    def get_feedback_log(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent feedback messages from Eos.

        Args:
            category: Filter by category (notify, error, event, etc.) or None for all
            limit: Maximum number of messages to return (default: 100)

        Returns:
            List of feedback message dictionaries
        """
        if not self.enable_rx:
            return []

        messages = self.feedback_log

        if category:
            messages = [m for m in messages if m['category'] == category]

        return messages[-limit:]

    def get_operator_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent operator actions for behavior learning.

        Args:
            limit: Maximum number of actions to return (default: 50)

        Returns:
            List of operator action dictionaries
        """
        if not self.enable_rx:
            return []

        return self.operator_actions[-limit:]

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent error messages - useful for learning what failed.

        Args:
            limit: Maximum number of errors to return (default: 10)

        Returns:
            List of error message dictionaries
        """
        return self.get_feedback_log(category='error', limit=limit)

    def clear_feedback_log(self) -> None:
        """Clear all stored feedback messages."""
        if self.enable_rx:
            self.feedback_log.clear()
            self.operator_actions.clear()
            logger.info("Feedback logs cleared")

    def start_receiver(self) -> None:
        """Start the OSC receiver server in a background thread."""
        if self.server:
            import threading
            server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            server_thread.start()
            logger.info("OSC receiver thread started")

    def shutdown(self) -> None:
        """Clean shutdown of OSC client and server."""
        if self.server:
            self.server.shutdown()
        logger.info("Eos OSC Client shutdown")
