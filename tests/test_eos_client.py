"""
Basic tests for Eos OSC Client

Run with: python -m pytest tests/
"""

import pytest
from src.eos_client import EosOSCClient
from src.utils.command_builder import (
    build_channel_selection,
    build_patch_command,
    build_cue_record_command,
    format_address
)


def test_eos_client_initialization():
    """Test Eos client can be initialized."""
    client = EosOSCClient(host="127.0.0.1", port=3032)
    assert client.host == "127.0.0.1"
    assert client.port == 3032
    assert client.user_id == 1


def test_channel_selection():
    """Test channel selection command building."""
    cmd = build_channel_selection(start=1)
    assert cmd == "Chan 1"
    
    cmd = build_channel_selection(start=1, end=10)
    assert cmd == "Chan 1 Thru 10"
    
    cmd = build_channel_selection(start=1, end=10, step=2)
    assert cmd == "Chan 1 Thru 10 Step 2"


def test_patch_command():
    """Test patch command building."""
    cmd = build_patch_command(channel=1, address="1/1")
    assert cmd == "Chan 1 Patch 1/1#"
    
    cmd = build_patch_command(channel=10, address="2/50", fixture_type="Source_Four")
    assert cmd == "Chan 10 Patch 2/50 Source_Four#"
    
    cmd = build_patch_command(channel=1, address="1/1", quantity=10)
    assert cmd == "Chan 1 Patch 1/1 Qty 10#"


def test_cue_record_command():
    """Test cue record command building."""
    cmd = build_cue_record_command(cue_number=10)
    assert cmd == "Record Cue 1/10#"
    
    cmd = build_cue_record_command(cue_number=1.5, label="My Cue")
    assert cmd == "Record Cue 1/1.5 Label My_Cue#"
    
    cmd = build_cue_record_command(cue_number=5, cue_list=2, blind=True)
    assert cmd == "Blind Record Cue 2/5#"


def test_address_formatting():
    """Test DMX address formatting."""
    addr = format_address(universe=1, address=1)
    assert addr == "1/1"
    
    addr = format_address(universe=2, address=256)
    assert addr == "2/256"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
