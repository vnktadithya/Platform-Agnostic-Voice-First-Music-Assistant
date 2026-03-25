import requests
import os
import time

def test_groq_connectivity():
    print("--- Groq-Azure Connectivity Diagnostic (2026) ---")
    
    # 1. Check basic DNS/SSL reachability
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    print(f"Testing reachability to: {api_url}")
    
    try:
        # Mock request to test connection (Unauthorized is fine, it means we reached the server)
        response = requests.get("https://api.groq.com", timeout=10)
        print(f"Status: {response.status_code} (Success: Connected to Groq/Cloudflare)")
    except Exception as e:
        print(f"Error: Could not reach Groq. This IP might be blocked. Detail: {e}")
        return

    # 2. Check full API authorization (if key exists)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Note: GROQ_API_KEY not found in .env, skipping auth test.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }

    print("Testing full API call...")
    try:
        start_time = time.time()
        resp = requests.post(api_url, headers=headers, json=payload, timeout=20)
        latency = (time.time() - start_time) * 1000
        
        if resp.status_code == 200:
            print(f"SUCCESS: Groq is fully operational from this Azure environment!")
            print(f"Latency: {latency:.2f}ms")
            print(f"Response: {resp.json()['choices'][0]['message']['content']}")
        elif resp.status_code == 403:
            print(f"BLOCKED: Groq/Cloudflare is blocking this Azure IP (403 Forbidden).")
        else:
            print(f"FAILED: Code {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"ERROR: API call failed. Details: {e}")

if __name__ == "__main__":
    test_groq_connectivity()
