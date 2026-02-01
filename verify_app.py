import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_verification():
    print("Starting verification...")
    
    # Session for Alice
    alice_session = requests.Session()
    # Session for Bob
    bob_session = requests.Session()

    # 1. Login Alice
    print("1. Logging in Alice...")
    res = alice_session.post(f"{BASE_URL}/login", data={"username": "Alice"})
    if res.status_code == 200:
        print("   -> Alice logged in successfully.")
    else:
        print(f"   -> Failed to login Alice: {res.status_code}")
        return

    # 2. Login Bob
    print("2. Logging in Bob...")
    res = bob_session.post(f"{BASE_URL}/login", data={"username": "Bob"})
    if res.status_code == 200:
        print("   -> Bob logged in successfully.")
    else:
        print(f"   -> Failed to login Bob: {res.status_code}")
        return

    # 3. Check User List (Alice looking for Bob)
    print("3. Alice checking user list...")
    res = alice_session.get(f"{BASE_URL}/api/users")
    users = res.json()
    bob_found = any(u['username'] == 'Bob' for u in users)
    if bob_found:
        print("   -> Alice sees Bob in user list.")
    else:
        print("   -> Alice DOES NOT see Bob (Failed).")

    # 4. Alice sends message to Bob
    print("4. Alice sending message to Bob...")
    msg_content = "Hello Bob, this is a test!"
    res = alice_session.post(f"{BASE_URL}/api/send", json={
        "recipient": "Bob",
        "content": msg_content
    })
    if res.status_code == 200:
        print("   -> Message sent.")
    else:
        print(f"   -> Failed to send message: {res.status_code}")

    # 5. Bob receives message
    print("5. Bob checking messages from Alice...")
    res = bob_session.get(f"{BASE_URL}/api/messages/Alice")
    messages = res.json()
    received_msg = next((m for m in messages if m['content'] == msg_content), None)
    
    if received_msg:
        print(f"   -> Bob received: '{received_msg['content']}'")
    else:
        print("   -> Bob did NOT receive the message (Failed).")

    print("\nVerification Complete.")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"Verification failed with error: {e}")
        print("Ensure the Flask app is running!")
