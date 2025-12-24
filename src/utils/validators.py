"""
Input Validators

Validation utilities for Eos-specific constraints and formats.
"""

from typing import Union


def validate_channel_number(channel: int) -> int:
    """
    Validate channel number is within acceptable range.
    
    Args:
        channel: Channel number to validate
    
    Returns:
        Validated channel number
    
    Raises:
        ValueError: If channel is out of range
    """
    if channel < 1 or channel > 99999:
        raise ValueError(f"Channel number must be between 1 and 99999, got {channel}")
    return channel


def validate_intensity(level: float) -> float:
    """
    Validate intensity level is within acceptable range.
    
    Args:
        level: Intensity level to validate (0-100)
    
    Returns:
        Validated intensity level
    
    Raises:
        ValueError: If level is out of range
    """
    if level < 0 or level > 100:
        raise ValueError(f"Intensity must be between 0 and 100, got {level}")
    return level


def validate_cue_number(cue_number: Union[int, float]) -> Union[int, float]:
    """
    Validate cue number format.
    
    Args:
        cue_number: Cue number to validate
    
    Returns:
        Validated cue number
    
    Raises:
        ValueError: If cue number is invalid
    """
    if isinstance(cue_number, (int, float)):
        if cue_number <= 0 or cue_number > 99999:
            raise ValueError(f"Cue number must be between 0 and 99999, got {cue_number}")
        return cue_number
    raise ValueError(f"Cue number must be int or float, got {type(cue_number)}")


def validate_dmx_address(universe: int, address: int) -> tuple:
    """
    Validate DMX address components.
    
    Args:
        universe: DMX universe number
        address: DMX address within universe
    
    Returns:
        Tuple of (universe, address)
    
    Raises:
        ValueError: If universe or address is out of range
    """
    if universe < 1 or universe > 255:
        raise ValueError(f"Universe must be between 1 and 255, got {universe}")
    if address < 1 or address > 512:
        raise ValueError(f"Address must be between 1 and 512, got {address}")
    return (universe, address)


def validate_time(time_value: float) -> float:
    """
    Validate timing value (fade, delay, follow).
    
    Args:
        time_value: Time in seconds
    
    Returns:
        Validated time value
    
    Raises:
        ValueError: If time is negative or unreasonably large
    """
    if time_value < 0:
        raise ValueError(f"Time cannot be negative, got {time_value}")
    if time_value > 3600:  # 1 hour max
        raise ValueError(f"Time exceeds maximum (3600 seconds), got {time_value}")
    return time_value


def validate_effect_rate(rate: float) -> float:
    """
    Validate effect rate value.
    
    Args:
        rate: Effect rate/speed
    
    Returns:
        Validated rate
    
    Raises:
        ValueError: If rate is out of acceptable range
    """
    if rate < 0.1 or rate > 1000:
        raise ValueError(f"Effect rate must be between 0.1 and 1000, got {rate}")
    return rate


def validate_effect_size(size: float) -> float:
    """
    Validate effect size/amplitude.
    
    Args:
        size: Effect size (typically 0-100)
    
    Returns:
        Validated size
    
    Raises:
        ValueError: If size is out of range
    """
    if size < 0 or size > 100:
        raise ValueError(f"Effect size must be between 0 and 100, got {size}")
    return size


def validate_palette_type(palette_type: str) -> str:
    """
    Validate palette type is one of the accepted types.
    
    Args:
        palette_type: Palette type string
    
    Returns:
        Validated and capitalized palette type
    
    Raises:
        ValueError: If palette type is not recognized
    """
    valid_types = ["Focus", "Color", "Beam", "Intensity"]
    capitalized = palette_type.capitalize()
    
    if capitalized not in valid_types:
        raise ValueError(
            f"Palette type must be one of {valid_types}, got '{palette_type}'"
        )
    return capitalized


def validate_user_id(user_id: int) -> int:
    """
    Validate Eos user ID.
    
    Args:
        user_id: User ID number
    
    Returns:
        Validated user ID
    
    Raises:
        ValueError: If user ID is out of range
    """
    if user_id < 1 or user_id > 999:
        raise ValueError(f"User ID must be between 1 and 999, got {user_id}")
    return user_id


def validate_label(label: str) -> str:
    """
    Validate and sanitize label/name strings for Eos.
    
    Args:
        label: Label string
    
    Returns:
        Sanitized label (spaces replaced with underscores)
    
    Raises:
        ValueError: If label is empty or too long
    """
    if not label or not label.strip():
        raise ValueError("Label cannot be empty")
    if len(label) > 100:
        raise ValueError(f"Label too long (max 100 chars), got {len(label)} chars")
    
    # Eos uses underscores for spaces in labels
    return label.strip().replace(" ", "_")
