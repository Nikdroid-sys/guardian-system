import httpx
import json

def test_server():
    url = "http://127.0.0.1:8000/mcp"
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    print(f"[*] Connecting to {url}...")
    try:
        # Use a context manager to handle the stream
        with httpx.stream("POST", url, json=payload, headers=headers, timeout=10.0) as response:
            print(f"[*] Status: {response.status_code}")
            
            if response.status_code == 200:
                print("[+] Connection Handshake Successful.")
                # Read the first chunk of the stream
                for line in response.iter_lines():
                    if line.startswith("data:"):
                        # MCP 2026 sends JSON-RPC inside 'data:' prefixes
                        data_str = line.replace("data:", "").strip()
                        tools_data = json.loads(data_str)
                        print("[+] Tools Found:")
                        print(json.dumps(tools_data, indent=2))
                        return # We got what we needed
            else:
                print(f"[-] Error: {response.status_code}")
                
    except Exception as e:
        print(f"[-] Protocol Error: {str(e)}")

if __name__ == "__main__":
    test_server()