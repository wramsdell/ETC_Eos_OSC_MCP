"""
Effects Management Tools

MCP tools for creating and managing effects in Eos.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import json

from utils.command_builder import (
    build_effect_command,
    build_delete_command,
    build_channel_selection
)
from utils.validators import (
    validate_effect_rate,
    validate_effect_size,
    validate_channel_number
)


class CreateEffectInput(BaseModel):
    """Input model for creating an effect."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    effect_number: int = Field(
        ...,
        description="Effect number to create (1-999)",
        ge=1,
        le=999
    )
    start_channel: int = Field(
        ...,
        description="Starting channel for effect",
        ge=1,
        le=99999
    )
    end_channel: int = Field(
        ...,
        description="Ending channel for effect",
        ge=1,
        le=99999
    )
    parameter: str = Field(
        default="Intens",
        description="Parameter to affect: Intens, Pan, Tilt, Color, etc.",
        max_length=50
    )
    rate: Optional[float] = Field(
        default=None,
        description="Effect rate/speed (0.1-1000)",
        ge=0.1,
        le=1000.0
    )
    size: Optional[float] = Field(
        default=None,
        description="Effect size/amplitude (0-100)",
        ge=0.0,
        le=100.0
    )
    waveform: Optional[str] = Field(
        default=None,
        description="Waveform type: Sine, Triangle, Square, Ramp, etc.",
        max_length=50
    )


class DeleteEffectInput(BaseModel):
    """Input model for deleting an effect."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    effect_number: int = Field(
        ...,
        description="Effect number to delete (1-999)",
        ge=1,
        le=999
    )


def register_effect_tools(mcp, eos_client):
    """
    Register effect management tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        eos_client: EosOSCClient instance
    """
    
    @mcp.tool(
        name="eos_create_effect",
        annotations={
            "title": "Create Lighting Effect",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_create_effect(params: CreateEffectInput) -> str:
        """Create a lighting effect on a range of channels.
        
        Build effects like chases, waves, and patterns that affect channel parameters
        over time. Common parameters include Intens, Pan, Tilt, Color, etc.
        
        Args:
            params (CreateEffectInput): Effect parameters containing:
                - effect_number (int): Effect number (1-999)
                - start_channel (int): Starting channel
                - end_channel (int): Ending channel
                - parameter (str): Parameter to affect (default: "Intens")
                - rate (Optional[float]): Effect rate/speed
                - size (Optional[float]): Effect size/amplitude
                - waveform (Optional[str]): Waveform type (Sine, Triangle, etc.)
        
        Returns:
            str: JSON response with effect creation status
        """
        try:
            # Validate channels
            validate_channel_number(params.start_channel)
            validate_channel_number(params.end_channel)
            
            if params.end_channel < params.start_channel:
                raise ValueError("End channel must be >= start channel")
            
            # Validate optional parameters
            if params.rate is not None:
                validate_effect_rate(params.rate)
            if params.size is not None:
                validate_effect_size(params.size)
            
            # Build channel selection
            channels = build_channel_selection(
                start=params.start_channel,
                end=params.end_channel
            )
            
            # Build and send effect command
            command = build_effect_command(
                effect_number=params.effect_number,
                channels=channels,
                parameter=params.parameter,
                rate=params.rate,
                size=params.size,
                waveform=params.waveform
            )
            
            eos_client.send_command(command)
            
            effect_params = {"parameter": params.parameter}
            if params.rate:
                effect_params["rate"] = params.rate
            if params.size:
                effect_params["size"] = params.size
            if params.waveform:
                effect_params["waveform"] = params.waveform
            
            result = {
                "success": True,
                "message": f"Created effect {params.effect_number}",
                "details": {
                    "effect_number": params.effect_number,
                    "channels": f"{params.start_channel}-{params.end_channel}",
                    "parameters": effect_params
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to create effect"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_delete_effect",
        annotations={
            "title": "Delete Effect",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_delete_effect(params: DeleteEffectInput) -> str:
        """Delete an effect.
        
        Permanently remove the specified effect. This operation cannot be easily undone.
        
        Args:
            params (DeleteEffectInput): Delete parameters containing:
                - effect_number (int): Effect number to delete
        
        Returns:
            str: JSON response with delete operation status
        """
        try:
            # Build and send delete command
            command = build_delete_command(
                target_type="Effect",
                target_number=params.effect_number
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Deleted effect {params.effect_number}",
                "warning": "This operation cannot be easily undone",
                "details": {
                    "effect_number": params.effect_number
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to delete effect"
            }
            return json.dumps(error, indent=2)
