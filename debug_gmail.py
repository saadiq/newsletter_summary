#!/usr/bin/env python3
"""Debug script to test Gmail authentication and fetch."""

import os
import json
from auth import authenticate_gmail
from fetch import get_ai_newsletters

def main():
    print("=== Gmail Debug Tool ===\n")
    
    # Check for credential files
    print("1. Checking credential files...")
    if os.path.exists('credentials.json'):
        print("✓ credentials.json found")
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            print(f"  Client ID: {creds.get('installed', {}).get('client_id', 'NOT FOUND')[:20]}...")
    else:
        print("✗ credentials.json NOT FOUND")
        return
    
    if os.path.exists('token.json'):
        print("✓ token.json found")
        with open('token.json', 'r') as f:
            token = json.load(f)
            print(f"  Token expires: {token.get('expiry', 'NO EXPIRY')}")
            print(f"  Scopes: {token.get('scopes', [])}")
    else:
        print("✗ token.json NOT FOUND")
        print("  You need to authenticate first by running: python main.py --days 1")
        return
    
    # Test authentication
    print("\n2. Testing Gmail authentication...")
    try:
        service = authenticate_gmail()
        print("✓ Gmail authentication successful")
    except Exception as e:
        print(f"✗ Gmail authentication failed: {e}")
        return
    
    # Test fetching
    print("\n3. Testing newsletter fetch...")
    try:
        print("Fetching newsletters from last 7 days with label 'ai-newsletter'...")
        newsletters = get_ai_newsletters(service, days=7, label='ai-newsletter')
        print(f"✓ Fetched {len(newsletters)} newsletters")
        
        if newsletters:
            print("\nFirst newsletter:")
            print(f"  Subject: {newsletters[0]['subject']}")
            print(f"  From: {newsletters[0]['sender']}")
            print(f"  Date: {newsletters[0]['date']}")
            print(f"  Body length: {len(newsletters[0].get('body', ''))} chars")
    except Exception as e:
        print(f"✗ Newsletter fetch failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main()