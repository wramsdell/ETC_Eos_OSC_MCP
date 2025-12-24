"""
Palette Management Tools

MCP tools for creating and managing palettes in Eos.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import json

from ..utils.command_builder import (
    build_palette_record_command,
    build_palette_apply_command,
    build_delete_command,
    build_channel_selection
)
from ..utils.validators import (
    validate_palette_type,
    validate_label,
    validate_channel_number
)


class RecordPaletteInput(BaseModel):
    """Input model for recording a palette."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    palette_number: int = Field(
        ...,
        description="Palette number to create (1-999)",
        ge=1,
        le=999
    )
    palette_type: str = Field(
        ...,
        description="Palette type: Focus, Color, Beam, or Intensity",
        max_length=20
    )
    label: Optional[str] = Field(
        default=None,
        description="Palette label/name",
        max_length=100
    )
    
    @field_validator('palette_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate palette type."""
        return validate_palette_type(v)


class ApplyPaletteInput(BaseModel):
    """Input model for applying a palette."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    palette_number: int = Field(
        ...,
        description="Palette number to apply (1-999)",
        ge=1,
        le=999
    )
    start_channel: Optional[int] = Field(
        default=None,
        description="Starting channel (optional, uses current selection if None)",
        ge=1,
        le=99999
    )
    end_channel: Optional[int] = Field(
        default=None,
        description="Ending channel for range (optional)",
        ge=1,
        le=99999
    )


class DeletePaletteInput(BaseModel):
    """Input model for deleting a palette."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    palette_number: int = Field(
        ...,
        description="Palette number to delete (1-999)",
        ge=1,
        le=999
    )


def register_palette_tools(mcp, eos_client):
    """
    Register palette management tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        eos_client: EosOSCClient instance
    """
    
    @mcp.tool(
        name="eos_record_palette",
        annotations={
            "title": "Record Palette",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_record_palette(params: RecordPaletteInput) -> str:
        """Record current parameter values as a palette.
        
        Create palettes for Focus (pan/tilt/zoom), Color, Beam (gobo/iris/shutter),
        or Intensity. Records currently selected channels and their parameter values.
        
        Args:
            params (RecordPaletteInput): Palette parameters containing:
                - palette_number (int): Palette number (1-999)
                - palette_type (str): Type (Focus, Color, Beam, Intensity)
                - label (Optional[str]): Palette label/name
        
        Returns:
            str: JSON response with record operation status
        """
        try:
            # Validate and format label if provided
            formatted_label = None
            if params.label:
                formatted_label = validate_label(params.label)
            
            # Build and send record command
            command = build_palette_record_command(
                palette_number=params.palette_number,
                palette_type=params.palette_type,
                label=formatted_label
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Recorded {params.palette_type} palette {params.palette_number}",
                "details": {
                    "palette_number": params.palette_number,
                    "type": params.palette_type,
                    "label": params.label
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to record palette"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_apply_palette",
        annotations={
            "title": "Apply Palette",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_apply_palette(params: ApplyPaletteInput) -> str:
        """Apply a palette to channels.
        
        Apply a previously recorded palette to the current channel selection or to
        a specified range of channels.
        
        Args:
            params (ApplyPaletteInput): Apply parameters containing:
                - palette_number (int): Palette number to apply
                - start_channel (Optional[int]): Starting channel (uses current selection if None)
                - end_channel (Optional[int]): Ending channel for range
        
        Returns:
            str: JSON response with apply operation status
        """
        try:
            # Build channel selection if specified
            channels = None
            if params.start_channel is not None:
                validate_channel_number(params.start_channel)
                
                if params.end_channel is not None:
                    validate_channel_number(params.end_channel)
                    if params.end_channel < params.start_channel:
                        raise ValueError("End channel must be >= start channel")
                
                channels = build_channel_selection(
                    start=params.start_channel,
                    end=params.end_channel
                )
            
            # Build and send apply command
            command = build_palette_apply_command(
                palette_number=params.palette_number,
                channels=channels
            )
            
            eos_client.send_command(command)
            
            details = {"palette_number": params.palette_number}
            if channels:
                if params.end_channel:
                    details["applied_to"] = f"channels {params.start_channel}-{params.end_channel}"
                else:
                    details["applied_to"] = f"channel {params.start_channel}"
            else:
                details["applied_to"] = "current selection"
            
            result = {
                "success": True,
                "message": f"Applied palette {params.palette_number}",
                "details": details,
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to apply palette"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_delete_palette",
        annotations={
            "title": "Delete Palette",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_delete_palette(params: DeletePaletteInput) -> str:
        """Delete a palette.
        
        Permanently remove the specified palette. This operation cannot be easily undone.
        
        Args:
            params (DeletePaletteInput): Delete parameters containing:
                - palette_number (int): Palette number to delete
        
        Returns:
            str: JSON response with delete operation status
        """
        try:
            # Build and send delete command
            command = build_delete_command(
                target_type="Preset",
                target_number=params.palette_number
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Deleted palette {params.palette_number}",
                "warning": "This operation cannot be easily undone",
                "details": {
                    "palette_number": params.palette_number
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to delete palette"
            }
            return json.dumps(error, indent=2)
