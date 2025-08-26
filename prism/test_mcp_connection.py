#!/usr/bin/env python3
"""Test MCP server connection"""

import json
import subprocess
import time

def test_mcp_server():
    """Test the MCP server with proper initialization"""
    
    # Start the server process
    process = subprocess.Popen(
        ['python3', '/Users/umasankrudhya/claude-automations/prism/src/prism_mcp_server_correct.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize request with proper params
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    try:
        # Send request
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Wait a bit for response
        time.sleep(0.5)
        
        # Try to read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("✅ Server responded:", json.dumps(response, indent=2))
            
            # Send list_tools request
            list_tools = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            process.stdin.write(json.dumps(list_tools) + '\n')
            process.stdin.flush()
            
            time.sleep(0.5)
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if 'result' in response and 'tools' in response['result']:
                    tools = response['result']['tools']
                    print(f"\n✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool.get('description', '')[:50]}...")
        else:
            print("❌ No response from server")
            stderr = process.stderr.read()
            if stderr:
                print("Stderr:", stderr)
    
    finally:
        process.terminate()
        process.wait(timeout=1)

if __name__ == "__main__":
    test_mcp_server()