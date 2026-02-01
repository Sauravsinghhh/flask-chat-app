import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_verification():
    print("Starting debug verification...")
    
    alice = requests.Session()
    bob = requests.Session()

    # Login
    print("Logging in Alice...")
    r = alice.post(f"{BASE_URL}/login", data={"username": "Alice"})
    print(f"Alice Login: {r.status_code}")

    print("Logging in Bob...")
    r = bob.post(f"{BASE_URL}/login", data={"username": "Bob"})
    print(f"Bob Login: {r.status_code}")

    # Alice sends to Bob
    print("Alice sending message...")
    r = alice.post(f"{BASE_URL}/api/send", json={"recipient": "Bob", "content": "Hello"})
    print(f"Send status: {r.status_code}")
    print(f"Send response: {r.text}")

    # Bob checks
    print("Bob checking messages...")
    r = bob.get(f"{BASE_URL}/api/messages/Alice")
    print(f"Bob Messages: {r.text}")
    
    # Alice checks (to see if she sees her own message)
    print("Alice checking messages...")
    r = alice.get(f"{BASE_URL}/api/messages/Bob")
    print(f"Alice Messages: {r.text}")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"Error: {e}")
