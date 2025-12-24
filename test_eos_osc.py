#!/usr/bin/env python3
"""
Test script for ETC Eos OSC command formatting
Tests different OSC command formats to find the correct one for patching
"""

from pythonosc import udp_client
import time

# Configuration
EOS_HOST = "127.0.0.1"
EOS_PORT = 8000

# Create OSC client
client = udp_client.SimpleUDPClient(EOS_HOST, EOS_PORT)

print(f"Testing OSC commands to Eos at {EOS_HOST}:{EOS_PORT}")
print("=" * 60)

# Test 1: Ping test
print("\n1. Testing connection with ping...")
try:
    client.send_message("/eos/ping", [])
    print("   ✓ Ping sent to /eos/ping")
    time.sleep(0.5)
except Exception as e:
    print(f"   ✗ Ping failed: {e}")

# Test 2: Clear command line test
print("\n2. Testing clear command line...")
try:
    client.send_message("/eos/key/clear", 1.0)
    print("   ✓ Clear sent to /eos/key/clear")
    time.sleep(1.0)
except Exception as e:
    print(f"   ✗ Clear failed: {e}")

# Test 3: Using /eos/newcmd (This is the recommended method from the docs)
print("\n3. Testing patch via /eos/newcmd...")
print("   (Check console command line now)")
try:
    client.send_message("/eos/key/clear", 1.0)
    time.sleep(0.5)
    
    patch_cmd = "Chan 1 Patch 1/1 42"
    client.send_message("/eos/newcmd", patch_cmd)
    print(f"   ✓ Command sent: {patch_cmd}")
    time.sleep(2.0)
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 4: Alternative - using /eos/cmd
print("\n4. Testing patch via /eos/cmd...")
print("   (Check console command line now)")
try:
    client.send_message("/eos/key/clear", 1.0)
    time.sleep(0.5)
    
    patch_cmd = "Chan 1 Patch 1/1 42"
    client.send_message("/eos/cmd", patch_cmd)
    print(f"   ✓ Command sent: {patch_cmd}")
    time.sleep(2.0)
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 5: Using $ prefix (command line mode)
print("\n5. Testing patch via $ prefix...")
print("   (Check console command line now)")
try:
    client.send_message("/eos/key/clear", 1.0)
    time.sleep(0.5)
    
    patch_cmd = "$ Chan 1 Patch 1/1 42#"
    client.send_message("/eos/newcmd", patch_cmd)
    print(f"   ✓ Command sent: {patch_cmd}")
    time.sleep(2.0)
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 6: Breaking it down into individual key presses
print("\n6. Testing patch via individual /eos/key commands...")
print("   (Watch console command line build up)")
try:
    client.send_message("/eos/key/clear", 1.0)
    time.sleep(0.5)
    
    print("   Sending: Chan")
    client.send_message("/eos/key/chan", 1.0)
    time.sleep(0.3)
    
    print("   Sending: 1")
    client.send_message("/eos/key/1", 1.0)
    time.sleep(0.3)
    
    print("   Sending: Patch")
    client.send_message("/eos/key/patch", 1.0)
    time.sleep(0.3)
    
    print("   Sending: 1 / 1")
    client.send_message("/eos/key/1", 1.0)
    time.sleep(0.2)
    client.send_message("/eos/key/slash", 1.0)
    time.sleep(0.2)
    client.send_message("/eos/key/1", 1.0)
    time.sleep(0.3)
    
    print("   Sending: 4 2")
    client.send_message("/eos/key/4", 1.0)
    time.sleep(0.2)
    client.send_message("/eos/key/2", 1.0)
    time.sleep(0.3)
    
    print("   Sending: Enter")
    client.send_message("/eos/key/enter", 1.0)
    
    print("   ✓ Individual keys sent")
    time.sleep(2.0)
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 7: Direct command format per OSC spec
print("\n7. Testing /eos/user/0/newcmd...")
print("   (Check console command line now)")
try:
    client.send_message("/eos/key/clear", 1.0)
    time.sleep(0.5)
    
    patch_cmd = "Chan 1 Patch 1/1 42"
    client.send_message("/eos/user/0/newcmd", patch_cmd)
    print(f"   ✓ Command sent to user 0: {patch_cmd}")
    time.sleep(2.0)
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("\nCheck your ETCnomad console to see which method worked.")
print("Look at the command line to see what was entered.")
print("\nNOTE: You may need to enable OSC RX in your console settings")
print("      and verify the port is set to 8000")
