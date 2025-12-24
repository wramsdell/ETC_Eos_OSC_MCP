#!/usr/bin/env python3
"""
Interactive OSC Command Shell for ETC Eos
Allows you to type OSC commands and send them to Eos
"""

from pythonosc import udp_client
import sys

# Configuration
EOS_HOST = "127.0.0.1"
EOS_PORT = 8000

# Create OSC client
client = udp_client.SimpleUDPClient(EOS_HOST, EOS_PORT)

print("=" * 60)
print("Interactive ETC Eos OSC Command Shell")
print("=" * 60)
print(f"Connected to: {EOS_HOST}:{EOS_PORT}")
print()
print("Commands:")
print("  /eos/... <args>     - Send OSC command with optional arguments")
print("  ping                - Send ping to Eos")
print("  clear               - Clear command line")
print("  help                - Show this help")
print("  quit                - Exit")
print()
print("Examples:")
print("  /eos/newcmd Chan 1 At 50")
print("  /eos/key/chan 1.0")
print("  /eos/chan 1")
print("=" * 60)
print()

while True:
    try:
        # Get user input
        cmd = input("OSC> ").strip()
        
        if not cmd:
            continue
            
        # Handle special commands
        if cmd.lower() == 'quit' or cmd.lower() == 'exit':
            print("Goodbye!")
            break
            
        if cmd.lower() == 'help':
            print()
            print("Commands:")
            print("  /eos/... <args>     - Send OSC command with optional arguments")
            print("  ping                - Send ping to Eos")
            print("  clear               - Clear command line")
            print("  help                - Show this help")
            print("  quit                - Exit")
            print()
            continue
            
        if cmd.lower() == 'ping':
            client.send_message("/eos/ping", [])
            print("✓ Ping sent")
            continue
            
        if cmd.lower() == 'clear':
            client.send_message("/eos/key/clear", 1.0)
            print("✓ Clear sent")
            continue
        
        # Parse OSC command
        parts = cmd.split(None, 1)  # Split on first whitespace
        osc_address = parts[0]
        
        # Check if it starts with /
        if not osc_address.startswith('/'):
            print("✗ OSC address must start with '/'")
            print("  Example: /eos/newcmd Chan 1 At 50")
            continue
        
        # Get the rest as a single string argument
        args = []
        if len(parts) > 1:
            args = [parts[1]]  # Send everything after the address as one string
        
        # Send the OSC message
        if args:
            client.send_message(osc_address, args)
            print(f"✓ Sent: {osc_address}={repr(args[0])}")
        else:
            client.send_message(osc_address, [])
            print(f"✓ Sent: {osc_address}")
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"✗ Error: {e}")
