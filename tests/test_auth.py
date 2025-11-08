#!/usr/bin/env python3
"""
Quick Twitter Auth Test - API Keys kontrolü
"""

import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

# Credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

print("=" * 60)
print("Twitter Authentication Test")
print("=" * 60)
print()

# Credentials göster (gizli)
print("Credentials loaded:")
print(f"  API Key: {api_key[:10]}...{api_key[-5:]}")
print(f"  API Secret: {api_secret[:10]}...{api_secret[-5:]}")
print(f"  Access Token: {access_token[:20]}...{access_token[-5:]}")
print(f"  Access Token Secret: {access_token_secret[:10]}...{access_token_secret[-5:]}")
print()

# Test 1: OAuth1 User Handler
print("Test 1: OAuth 1.0a User Authentication")
try:
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret,
        access_token, access_token_secret
    )
    api = tweepy.API(auth)
    
    # Get authenticated user info
    me = api.verify_credentials()
    print(f"  ✅ Successfully authenticated as: @{me.screen_name}")
    print(f"  Account name: {me.name}")
    print(f"  Followers: {me.followers_count}")
    print()
except Exception as e:
    print(f"  ❌ OAuth1 Authentication failed: {e}")
    print()

# Test 2: Client (v2 API)
print("Test 2: Twitter API v2 Client")
try:
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # Get authenticated user
    me = client.get_me()
    if me.data:
        print(f"  ✅ Successfully authenticated")
        print(f"  User ID: {me.data.id}")
        print(f"  Username: @{me.data.username}")
    else:
        print(f"  ❌ No user data returned")
    print()
except Exception as e:
    print(f"  ❌ Client authentication failed: {e}")
    print()

print("=" * 60)
print("Test completed!")
print("=" * 60)
