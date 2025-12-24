"""
Patch Management Tools

MCP tools for patching, unpatching, and managing fixtures in Eos.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import json

from ..utils.command_builder import (
    build_patch_command,
    build_unpatch_command,
    format_address
)
from ..utils.validators import (
    validate_channel_number,
    validate_dmx_address
)


class PatchFixtureInput(BaseModel):
    """Input model for patching a fixture."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    channel: int = Field(
        ...,
        description="Channel number to patch (1-99999)",
        ge=1,
        le=99999
    )
    universe: int = Field(
        ...,
        description="DMX universe number (1-255)",
        ge=1,
        le=255
    )
    address: int = Field(
        ...,
        description="DMX address within universe (1-512)",
        ge=1,
        le=512
    )
    fixture_type: Optional[str] = Field(
        default=None,
        description="Fixture type name or number from Eos library (e.g., 'Source_Four_LED', '405')",
        max_length=100
    )
    quantity: int = Field(
        default=1,
        description="Number of fixtures to patch sequentially (default: 1)",
        ge=1,
        le=100
    )
    
    @field_validator('universe', 'address')
    @classmethod
    def validate_dmx(cls, v: int, info) -> int:
        """Validate DMX addressing."""
        return v


class UnpatchChannelInput(BaseModel):
    """Input model for unpatching channels."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    start_channel: int = Field(
        ...,
        description="Starting channel number to unpatch (1-99999)",
        ge=1,
        le=99999
    )
    end_channel: Optional[int] = Field(
        default=None,
        description="Ending channel for range unpatch (optional)",
        ge=1,
        le=99999
    )


class SetFixturePositionInput(BaseModel):
    """Input model for setting Augment3d fixture position."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    channel: int = Field(
        ...,
        description="Channel number to position (1-99999)",
        ge=1,
        le=99999
    )
    x: float = Field(
        ...,
        description="X coordinate in meters (stage left/right, negative is left)",
    )
    y: float = Field(
        ...,
        description="Y coordinate in meters (upstage/downstage, positive is upstage)",
    )
    z: float = Field(
        ...,
        description="Z coordinate in meters (height above stage)",
        ge=0.0
    )
    pan: float = Field(
        default=0.0,
        description="Pan orientation in degrees (0-360)",
        ge=0.0,
        le=360.0
    )
    tilt: float = Field(
        default=0.0,
        description="Tilt orientation in degrees (0-360)",
        ge=0.0,
        le=360.0
    )
    roll: float = Field(
        default=0.0,
        description="Roll orientation in degrees (0-360)",
        ge=0.0,
        le=360.0
    )


class GetPatchInfoInput(BaseModel):
    """Input model for querying patch information."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    channel: int = Field(
        ...,
        description="Channel number to query (1-99999)",
        ge=1,
        le=99999
    )


def register_patch_tools(mcp, eos_client):
    """
    Register patch management tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        eos_client: EosOSCClient instance
    """
    
    @mcp.tool(
        name="eos_patch_fixture",
        annotations={
            "title": "Patch Fixture to Channel",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_patch_fixture(params: PatchFixtureInput) -> str:
        """Patch a lighting fixture to a channel with DMX address.
        
        This tool assigns a fixture type to a channel number and gives it a DMX address
        in Augment3d and the patch. If quantity > 1, fixtures are patched sequentially
        with incrementing channels and addresses.
        
        Args:
            params (PatchFixtureInput): Patch parameters containing:
                - channel (int): Channel number (1-99999)
                - universe (int): DMX universe (1-255)
                - address (int): DMX address in universe (1-512)
                - fixture_type (Optional[str]): Fixture type from Eos library
                - quantity (int): Number of fixtures to patch (default: 1)
        
        Returns:
            str: JSON response with patch operation status
        """
        try:
            # Validate inputs
            validate_channel_number(params.channel)
            validate_dmx_address(params.universe, params.address)
            
            # Build DMX address string
            dmx_address = format_address(params.universe, params.address)
            
            # Build and send patch command
            command = build_patch_command(
                channel=params.channel,
                address=dmx_address,
                fixture_type=params.fixture_type,
                quantity=params.quantity
            )
            
            eos_client.send_command(command)
            
            # Build response
            result = {
                "success": True,
                "message": f"Patched channel(s) starting at {params.channel}",
                "details": {
                    "channel": params.channel,
                    "dmx_address": dmx_address,
                    "fixture_type": params.fixture_type or "Generic",
                    "quantity": params.quantity
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to patch fixture"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_unpatch_channel",
        annotations={
            "title": "Unpatch Channel(s)",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_unpatch_channel(params: UnpatchChannelInput) -> str:
        """Remove fixture(s) from patch.
        
        Unpatch a single channel or a range of channels, removing their DMX addressing
        and fixture assignments.
        
        Args:
            params (UnpatchChannelInput): Unpatch parameters containing:
                - start_channel (int): Starting channel to unpatch
                - end_channel (Optional[int]): End channel for range (optional)
        
        Returns:
            str: JSON response with unpatch operation status
        """
        try:
            # Validate inputs
            validate_channel_number(params.start_channel)
            if params.end_channel:
                validate_channel_number(params.end_channel)
                if params.end_channel < params.start_channel:
                    raise ValueError("End channel must be >= start channel")
            
            # Build and send unpatch command
            command = build_unpatch_command(
                start=params.start_channel,
                end=params.end_channel
            )
            
            eos_client.send_command(command)
            
            # Build response
            if params.end_channel:
                message = f"Unpatched channels {params.start_channel} through {params.end_channel}"
                count = params.end_channel - params.start_channel + 1
            else:
                message = f"Unpatched channel {params.start_channel}"
                count = 1
            
            result = {
                "success": True,
                "message": message,
                "details": {
                    "start_channel": params.start_channel,
                    "end_channel": params.end_channel,
                    "channels_affected": count
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to unpatch channel(s)"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_set_fixture_position",
        annotations={
            "title": "Set Fixture Position in Augment3d",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_set_fixture_position(params: SetFixturePositionInput) -> str:
        """Set the 3D position and orientation of a fixture in Augment3d.
        
        Position fixtures in the 3D visualization space with X, Y, Z coordinates
        and pan, tilt, roll orientation. Coordinates are in meters.
        
        Coordinate system:
        - X: Stage left (-) to right (+)
        - Y: Downstage (-) to upstage (+)  
        - Z: Height above stage (always positive)
        
        Args:
            params (SetFixturePositionInput): Position parameters containing:
                - channel (int): Channel number to position
                - x (float): X coordinate in meters
                - y (float): Y coordinate in meters
                - z (float): Z coordinate in meters (height)
                - pan (float): Pan orientation 0-360° (default: 0)
                - tilt (float): Tilt orientation 0-360° (default: 0)
                - roll (float): Roll orientation 0-360° (default: 0)
        
        Returns:
            str: JSON response with position update status
        """
        try:
            # Validate channel
            validate_channel_number(params.channel)
            
            # Set position via OSC
            eos_client.set_patch_position(
                channel=params.channel,
                x=params.x,
                y=params.y,
                z=params.z,
                pan=params.pan,
                tilt=params.tilt,
                roll=params.roll
            )
            
            result = {
                "success": True,
                "message": f"Set position for channel {params.channel}",
                "details": {
                    "channel": params.channel,
                    "position": {
                        "x": params.x,
                        "y": params.y,
                        "z": params.z
                    },
                    "orientation": {
                        "pan": params.pan,
                        "tilt": params.tilt,
                        "roll": params.roll
                    }
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to set fixture position"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_get_patch_info",
        annotations={
            "title": "Get Patch Information",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_get_patch_info(params: GetPatchInfoInput) -> str:
        """Request patch information for a channel.
        
        Note: This sends a query to the console. If OSC RX is not enabled,
        the response won't be received. This is primarily useful when the
        EosOSCClient has receive capabilities enabled.
        
        Args:
            params (GetPatchInfoInput): Query parameters containing:
                - channel (int): Channel number to query
        
        Returns:
            str: JSON response indicating query was sent
        """
        try:
            # Validate channel
            validate_channel_number(params.channel)
            
            # Request position information
            eos_client.get_patch_position(params.channel)
            
            result = {
                "success": True,
                "message": f"Requested patch info for channel {params.channel}",
                "note": "Enable OSC RX on the EosOSCClient to receive the response",
                "details": {
                    "channel": params.channel
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to request patch information"
            }
            return json.dumps(error, indent=2)
