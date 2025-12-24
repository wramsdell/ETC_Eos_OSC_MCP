"""
Eos Command Builder Utilities

Helper functions for constructing properly formatted Eos command line syntax.
These utilities ensure commands follow Eos conventions and syntax rules.
"""

from typing import Optional, List, Union


def build_channel_selection(start: int, end: Optional[int] = None, step: Optional[int] = None) -> str:
    """
    Build channel selection syntax.
    
    Args:
        start: Starting channel number
        end: Ending channel for range (optional)
        step: Step value for selection (optional)
    
    Returns:
        Command string like "Chan 1" or "Chan 1 Thru 10" or "Chan 1 Thru 10 Step 2"
    """
    cmd = f"Chan {start}"
    if end is not None:
        cmd += f" Thru {end}"
    if step is not None:
        cmd += f" Step {step}"
    return cmd


def build_channel_list(channels: List[int]) -> str:
    """
    Build channel list syntax.
    
    Args:
        channels: List of channel numbers
    
    Returns:
        Command string like "Chan 1 + 5 + 10 + 15"
    """
    return "Chan " + " + ".join(str(ch) for ch in channels)


def build_intensity_command(level: float, channels: str = None) -> str:
    """
    Build intensity setting command.
    
    Args:
        level: Intensity level (0-100)
        channels: Channel selection string (optional, for direct command)
    
    Returns:
        Command string like "At 75" or "Chan 1 At 75#"
    """
    if channels:
        return f"{channels} At {level}#"
    else:
        return f"At {level}"


def build_patch_command(
    channel: int,
    address: str,
    fixture_type: Optional[str] = None,
    quantity: int = 1
) -> str:
    """
    Build fixture patching command.
    
    Args:
        channel: Starting channel number
        address: DMX address in format "universe/address" (e.g., "1/1")
        fixture_type: Fixture type name or number (optional)
        quantity: Number of fixtures to patch (default: 1)
    
    Returns:
        Command string like "Chan 1 Patch 1/1#" or "Chan 1 Patch 1/1 Fixture_Type Qty 10#"
    """
    cmd = f"Chan {channel} Patch {address}"
    if fixture_type:
        cmd += f" {fixture_type}"
    if quantity > 1:
        cmd += f" Qty {quantity}"
    cmd += "#"
    return cmd


def build_unpatch_command(start: int, end: Optional[int] = None) -> str:
    """
    Build unpatch command.
    
    Args:
        start: Starting channel number
        end: Ending channel (optional, for range)
    
    Returns:
        Command string like "Chan 1 Patch -#" or "Chan 1 Thru 10 Patch -#"
    """
    if end is not None:
        return f"Chan {start} Thru {end} Patch -#"
    else:
        return f"Chan {start} Patch -#"


def build_cue_record_command(
    cue_number: Union[int, float],
    cue_list: int = 1,
    label: Optional[str] = None,
    blind: bool = False
) -> str:
    """
    Build cue recording command.
    
    Args:
        cue_number: Cue number (can be decimal like 1.5)
        cue_list: Cue list number (default: 1)
        label: Cue label/name (optional)
        blind: Record in blind mode (default: False)
    
    Returns:
        Command string like "Record Cue 10#" or "Blind Record Cue 1.5 Label My_Cue#"
    """
    cmd = ""
    if blind:
        cmd += "Blind "
    
    cmd += f"Record Cue {cue_list}/{cue_number}"
    
    if label:
        # Replace spaces with underscores for Eos syntax
        safe_label = label.replace(" ", "_")
        cmd += f" Label {safe_label}"
    
    cmd += "#"
    return cmd


def build_cue_update_command(
    cue_number: Union[int, float],
    cue_list: int = 1,
    blind: bool = False
) -> str:
    """
    Build cue update command.
    
    Args:
        cue_number: Cue number to update
        cue_list: Cue list number (default: 1)
        blind: Update in blind mode (default: False)
    
    Returns:
        Command string like "Update Cue 10#" or "Blind Update Cue 1.5#"
    """
    cmd = ""
    if blind:
        cmd += "Blind "
    
    cmd += f"Update Cue {cue_list}/{cue_number}#"
    return cmd


def build_cue_timing_command(
    cue_number: Union[int, float],
    cue_list: int = 1,
    fade_time: Optional[float] = None,
    delay_time: Optional[float] = None,
    follow_time: Optional[float] = None
) -> str:
    """
    Build cue timing command.
    
    Args:
        cue_number: Cue number to modify
        cue_list: Cue list number (default: 1)
        fade_time: Fade time in seconds (optional)
        delay_time: Delay time in seconds (optional)
        follow_time: Follow time in seconds (optional)
    
    Returns:
        Command string like "Cue 10 Time 3 Delay 1#"
    """
    cmd = f"Cue {cue_list}/{cue_number}"
    
    if fade_time is not None:
        cmd += f" Time {fade_time}"
    if delay_time is not None:
        cmd += f" Delay {delay_time}"
    if follow_time is not None:
        cmd += f" Follow {follow_time}"
    
    cmd += "#"
    return cmd


def build_effect_command(
    effect_number: int,
    channels: str,
    parameter: str = "Intens",
    rate: Optional[float] = None,
    size: Optional[float] = None,
    waveform: Optional[str] = None
) -> str:
    """
    Build effect creation command.
    
    Args:
        effect_number: Effect number to create
        channels: Channel selection string
        parameter: Parameter to affect (default: "Intens")
        rate: Effect rate/speed (optional)
        size: Effect size/amplitude (optional)
        waveform: Waveform type like "Sine", "Triangle", "Square" (optional)
    
    Returns:
        Command string like "Effect 1 Chan 1 Thru 10 Param Intens Rate 2 Size 50#"
    """
    cmd = f"Effect {effect_number} {channels} Param {parameter}"
    
    if rate is not None:
        cmd += f" Rate {rate}"
    if size is not None:
        cmd += f" Size {size}"
    if waveform is not None:
        cmd += f" Waveform {waveform}"
    
    cmd += "#"
    return cmd


def build_palette_record_command(
    palette_number: int,
    palette_type: str,
    label: Optional[str] = None
) -> str:
    """
    Build palette recording command.
    
    Args:
        palette_number: Palette number to create
        palette_type: Type of palette ("Focus", "Color", "Beam", "Intensity")
        label: Palette label (optional)
    
    Returns:
        Command string like "Record Preset 5 Focus#" or "Record Preset 10 Color Label Blue#"
    """
    cmd = f"Record Preset {palette_number} {palette_type}"
    
    if label:
        safe_label = label.replace(" ", "_")
        cmd += f" Label {safe_label}"
    
    cmd += "#"
    return cmd


def build_palette_apply_command(
    palette_number: int,
    channels: Optional[str] = None
) -> str:
    """
    Build palette application command.
    
    Args:
        palette_number: Palette number to apply
        channels: Channel selection (optional, uses current selection if None)
    
    Returns:
        Command string like "Preset 5#" or "Chan 1 Thru 10 Preset 5#"
    """
    if channels:
        return f"{channels} Preset {palette_number}#"
    else:
        return f"Preset {palette_number}#"


def build_group_record_command(
    group_number: int,
    label: Optional[str] = None
) -> str:
    """
    Build group recording command.
    
    Args:
        group_number: Group number to create
        label: Group label (optional)
    
    Returns:
        Command string like "Record Group 5#" or "Record Group 10 Label Movers#"
    """
    cmd = f"Record Group {group_number}"
    
    if label:
        safe_label = label.replace(" ", "_")
        cmd += f" Label {safe_label}"
    
    cmd += "#"
    return cmd


def build_delete_command(
    target_type: str,
    target_number: Union[int, float],
    cue_list: Optional[int] = None
) -> str:
    """
    Build delete command for various targets.
    
    Args:
        target_type: Type to delete ("Cue", "Preset", "Group", "Effect", etc.)
        target_number: Number of item to delete
        cue_list: Cue list number (only for cues, optional)
    
    Returns:
        Command string like "Delete Cue 10#" or "Delete Preset 5#"
    """
    if target_type == "Cue" and cue_list is not None:
        return f"Delete {target_type} {cue_list}/{target_number}#"
    else:
        return f"Delete {target_type} {target_number}#"


def format_address(universe: int, address: int) -> str:
    """
    Format DMX address in Eos format.
    
    Args:
        universe: DMX universe (1-based)
        address: DMX address within universe (1-512)
    
    Returns:
        Formatted address like "1/1" or "2/256"
    """
    return f"{universe}/{address}"


def parse_cue_number(cue_str: str) -> Union[int, float]:
    """
    Parse cue number string to int or float.
    
    Args:
        cue_str: Cue number as string (e.g., "10" or "1.5")
    
    Returns:
        Cue number as int or float
    """
    if "." in cue_str:
        return float(cue_str)
    else:
        return int(cue_str)
