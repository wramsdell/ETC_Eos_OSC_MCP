"""
Cue Management Tools

MCP tools for creating, updating, and managing cues in Eos.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Union
import json

from ..utils.command_builder import (
    build_cue_record_command,
    build_cue_update_command,
    build_cue_timing_command,
    build_delete_command,
    parse_cue_number
)
from ..utils.validators import (
    validate_cue_number,
    validate_time,
    validate_label
)


class RecordCueInput(BaseModel):
    """Input model for recording a cue."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    cue_number: Union[int, float] = Field(
        ...,
        description="Cue number (can be decimal like 1.5 for point cues)",
    )
    cue_list: int = Field(
        default=1,
        description="Cue list number (default: 1)",
        ge=1,
        le=999
    )
    label: Optional[str] = Field(
        default=None,
        description="Cue label/name",
        max_length=100
    )
    blind: bool = Field(
        default=False,
        description="Record in blind mode (doesn't affect live output)"
    )


class UpdateCueInput(BaseModel):
    """Input model for updating a cue."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    cue_number: Union[int, float] = Field(
        ...,
        description="Cue number to update",
    )
    cue_list: int = Field(
        default=1,
        description="Cue list number (default: 1)",
        ge=1,
        le=999
    )
    blind: bool = Field(
        default=False,
        description="Update in blind mode"
    )


class SetCueTimingInput(BaseModel):
    """Input model for setting cue timing."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    cue_number: Union[int, float] = Field(
        ...,
        description="Cue number to modify",
    )
    cue_list: int = Field(
        default=1,
        description="Cue list number (default: 1)",
        ge=1,
        le=999
    )
    fade_time: Optional[float] = Field(
        default=None,
        description="Fade time in seconds",
        ge=0.0,
        le=3600.0
    )
    delay_time: Optional[float] = Field(
        default=None,
        description="Delay time before fade starts (seconds)",
        ge=0.0,
        le=3600.0
    )
    follow_time: Optional[float] = Field(
        default=None,
        description="Auto-follow time after previous cue (seconds)",
        ge=0.0,
        le=3600.0
    )


class FireCueInput(BaseModel):
    """Input model for firing a cue."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    cue_number: Union[int, float] = Field(
        ...,
        description="Cue number to fire",
    )
    cue_list: int = Field(
        default=1,
        description="Cue list number (default: 1)",
        ge=1,
        le=999
    )


class DeleteCueInput(BaseModel):
    """Input model for deleting a cue."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    cue_number: Union[int, float] = Field(
        ...,
        description="Cue number to delete",
    )
    cue_list: int = Field(
        default=1,
        description="Cue list number (default: 1)",
        ge=1,
        le=999
    )


def register_cue_tools(mcp, eos_client):
    """
    Register cue management tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        eos_client: EosOSCClient instance
    """
    
    @mcp.tool(
        name="eos_record_cue",
        annotations={
            "title": "Record Cue",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_record_cue(params: RecordCueInput) -> str:
        """Record current console state as a cue.
        
        Records all selected channels and their current parameter values into a cue.
        Can be recorded in blind mode to avoid affecting live output. Supports
        decimal cue numbers for point cues (e.g., 1.5, 2.3).
        
        Args:
            params (RecordCueInput): Record parameters containing:
                - cue_number (Union[int, float]): Cue number (e.g., 10 or 1.5)
                - cue_list (int): Cue list number (default: 1)
                - label (Optional[str]): Cue label/name
                - blind (bool): Record in blind mode (default: False)
        
        Returns:
            str: JSON response with record operation status
        """
        try:
            # Validate cue number
            validate_cue_number(params.cue_number)
            
            # Validate and format label if provided
            formatted_label = None
            if params.label:
                formatted_label = validate_label(params.label)
            
            # Build and send record command
            command = build_cue_record_command(
                cue_number=params.cue_number,
                cue_list=params.cue_list,
                label=formatted_label,
                blind=params.blind
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Recorded cue {params.cue_list}/{params.cue_number}",
                "details": {
                    "cue_number": params.cue_number,
                    "cue_list": params.cue_list,
                    "label": params.label,
                    "blind": params.blind
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to record cue"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_update_cue",
        annotations={
            "title": "Update Existing Cue",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_update_cue(params: UpdateCueInput) -> str:
        """Update an existing cue with current console state.
        
        Updates the specified cue with current channel selections and values.
        Only selected channels are updated; other channels in the cue remain unchanged.
        
        Args:
            params (UpdateCueInput): Update parameters containing:
                - cue_number (Union[int, float]): Cue number to update
                - cue_list (int): Cue list number (default: 1)
                - blind (bool): Update in blind mode (default: False)
        
        Returns:
            str: JSON response with update operation status
        """
        try:
            # Validate cue number
            validate_cue_number(params.cue_number)
            
            # Build and send update command
            command = build_cue_update_command(
                cue_number=params.cue_number,
                cue_list=params.cue_list,
                blind=params.blind
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Updated cue {params.cue_list}/{params.cue_number}",
                "details": {
                    "cue_number": params.cue_number,
                    "cue_list": params.cue_list,
                    "blind": params.blind
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to update cue"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_set_cue_timing",
        annotations={
            "title": "Set Cue Timing Parameters",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_set_cue_timing(params: SetCueTimingInput) -> str:
        """Set timing parameters for a cue.
        
        Configure fade time, delay time, and auto-follow timing for a cue.
        All times are in seconds. At least one timing parameter must be specified.
        
        Args:
            params (SetCueTimingInput): Timing parameters containing:
                - cue_number (Union[int, float]): Cue number to modify
                - cue_list (int): Cue list number (default: 1)
                - fade_time (Optional[float]): Fade time in seconds
                - delay_time (Optional[float]): Delay before fade starts (seconds)
                - follow_time (Optional[float]): Auto-follow after previous cue (seconds)
        
        Returns:
            str: JSON response with timing update status
        """
        try:
            # Validate cue number
            validate_cue_number(params.cue_number)
            
            # Validate timing values if provided
            if params.fade_time is not None:
                validate_time(params.fade_time)
            if params.delay_time is not None:
                validate_time(params.delay_time)
            if params.follow_time is not None:
                validate_time(params.follow_time)
            
            # Check at least one timing parameter is set
            if all(t is None for t in [params.fade_time, params.delay_time, params.follow_time]):
                raise ValueError("At least one timing parameter must be specified")
            
            # Build and send timing command
            command = build_cue_timing_command(
                cue_number=params.cue_number,
                cue_list=params.cue_list,
                fade_time=params.fade_time,
                delay_time=params.delay_time,
                follow_time=params.follow_time
            )
            
            eos_client.send_command(command)
            
            timing_details = {}
            if params.fade_time is not None:
                timing_details["fade"] = f"{params.fade_time}s"
            if params.delay_time is not None:
                timing_details["delay"] = f"{params.delay_time}s"
            if params.follow_time is not None:
                timing_details["follow"] = f"{params.follow_time}s"
            
            result = {
                "success": True,
                "message": f"Set timing for cue {params.cue_list}/{params.cue_number}",
                "details": {
                    "cue_number": params.cue_number,
                    "cue_list": params.cue_list,
                    "timing": timing_details
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to set cue timing"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_fire_cue",
        annotations={
            "title": "Fire/Execute Cue",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def eos_fire_cue(params: FireCueInput) -> str:
        """Execute/fire a specific cue.
        
        Fires the specified cue, causing it to execute with its programmed timing.
        This is equivalent to selecting the cue and pressing GO.
        
        Args:
            params (FireCueInput): Fire parameters containing:
                - cue_number (Union[int, float]): Cue number to fire
                - cue_list (int): Cue list number (default: 1)
        
        Returns:
            str: JSON response with fire operation status
        """
        try:
            # Validate cue number
            validate_cue_number(params.cue_number)
            
            # Fire cue via OSC
            eos_client.fire_cue(
                cue_number=params.cue_number,
                cue_list=params.cue_list
            )
            
            result = {
                "success": True,
                "message": f"Fired cue {params.cue_list}/{params.cue_number}",
                "details": {
                    "cue_number": params.cue_number,
                    "cue_list": params.cue_list
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to fire cue"
            }
            return json.dumps(error, indent=2)
    
    @mcp.tool(
        name="eos_delete_cue",
        annotations={
            "title": "Delete Cue",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def eos_delete_cue(params: DeleteCueInput) -> str:
        """Delete a cue from the cue list.
        
        Permanently removes the specified cue. This operation cannot be easily undone.
        
        Args:
            params (DeleteCueInput): Delete parameters containing:
                - cue_number (Union[int, float]): Cue number to delete
                - cue_list (int): Cue list number (default: 1)
        
        Returns:
            str: JSON response with delete operation status
        """
        try:
            # Validate cue number
            validate_cue_number(params.cue_number)
            
            # Build and send delete command
            command = build_delete_command(
                target_type="Cue",
                target_number=params.cue_number,
                cue_list=params.cue_list
            )
            
            eos_client.send_command(command)
            
            result = {
                "success": True,
                "message": f"Deleted cue {params.cue_list}/{params.cue_number}",
                "warning": "This operation cannot be easily undone",
                "details": {
                    "cue_number": params.cue_number,
                    "cue_list": params.cue_list
                },
                "command_sent": command
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error = {
                "success": False,
                "error": str(e),
                "message": "Failed to delete cue"
            }
            return json.dumps(error, indent=2)
