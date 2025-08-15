#!/usr/bin/env python3
"""
Helper script to prepare GitHub secrets from local credential files.
This ensures proper JSON formatting for GitHub Actions.
"""

import json
import os
import base64

def main():
    print("=== GitHub Secrets Preparation Tool ===\n")
    
    secrets = {}
    
    # Process credentials.json
    if os.path.exists('credentials.json'):
        print("Processing credentials.json...")
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        # Ensure it's properly formatted JSON
        secrets['GMAIL_CREDENTIALS'] = json.dumps(creds, separators=(',', ':'))
        print("✓ GMAIL_CREDENTIALS prepared")
    else:
        print("✗ credentials.json not found")
        print("  Please ensure credentials.json exists in the current directory")
        return
    
    # Process token.json
    if os.path.exists('token.json'):
        print("Processing token.json...")
        with open('token.json', 'r') as f:
            token = json.load(f)
        # Ensure it's properly formatted JSON
        secrets['GMAIL_TOKEN'] = json.dumps(token, separators=(',', ':'))
        print("✓ GMAIL_TOKEN prepared")
    else:
        print("✗ token.json not found")
        print("  Please run 'python main.py --days 1' to generate token.json")
        return
    
    # Get OpenRouter API key from environment
    openrouter_key = os.environ.get('OPENROUTER_API_KEY')
    if not openrouter_key:
        # Try to read from .env.local
        if os.path.exists('.env.local'):
            with open('.env.local', 'r') as f:
                for line in f:
                    if line.startswith('OPENROUTER_API_KEY='):
                        openrouter_key = line.split('=', 1)[1].strip()
                        break
    
    if openrouter_key:
        secrets['OPENROUTER_API_KEY'] = openrouter_key
        print("✓ OPENROUTER_API_KEY found")
    else:
        print("⚠ OPENROUTER_API_KEY not found in environment")
    
    # Save to file for easy copying
    print("\n=== Saving Secrets ===")
    
    with open('github_secrets.txt', 'w') as f:
        f.write("COPY THESE VALUES TO GITHUB SECRETS:\n")
        f.write("=====================================\n\n")
        
        for key, value in secrets.items():
            f.write(f"{key}:\n")
            f.write("-" * 40 + "\n")
            f.write(value + "\n")
            f.write("-" * 40 + "\n\n")
    
    print("✓ Secrets saved to github_secrets.txt")
    print("\nInstructions:")
    print("1. Open github_secrets.txt")
    print("2. For each secret, copy the value between the dashed lines")
    print("3. Go to your GitHub repo → Settings → Secrets → Actions")
    print("4. Add/update each secret with the exact name and copied value")
    print("5. Delete github_secrets.txt after adding secrets (contains sensitive data)")
    
    # Also create a validation script
    print("\n=== Creating Validation Script ===")
    
    validation_script = '''#!/bin/bash
# Test script to validate GitHub secrets format
echo "Testing JSON parsing..."

# Test credentials.json
echo "$GMAIL_CREDENTIALS" | python -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ GMAIL_CREDENTIALS is valid JSON"
else
    echo "✗ GMAIL_CREDENTIALS is invalid JSON"
fi

# Test token.json  
echo "$GMAIL_TOKEN" | python -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ GMAIL_TOKEN is valid JSON"
else
    echo "✗ GMAIL_TOKEN is invalid JSON"
fi

# Test OpenRouter key
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "✓ OPENROUTER_API_KEY is set"
else
    echo "✗ OPENROUTER_API_KEY is not set"
fi
'''
    
    with open('test_secrets.sh', 'w') as f:
        f.write(validation_script)
    os.chmod('test_secrets.sh', 0o755)
    
    print("✓ Created test_secrets.sh for validating secrets in GitHub Actions")
    print("\nYou can add this as a step in your workflow to debug secret issues")

if __name__ == "__main__":
    main()