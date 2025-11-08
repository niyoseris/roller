"""
Test roll.wiki API submission
"""
import asyncio
import aiohttp

async def test_rollwiki():
    """Test roll.wiki API with GET request"""
    
    url = "https://roll.wiki/api/v1/summarize"
    # Try NBA (should work)
    params = {
        "url": "https://en.wikipedia.org/wiki/NBA",
        "save": "true",
        "category": "Sports",
        "secret": "laylaylom"
    }
    
    print("🧪 Testing roll.wiki API...")
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    print()
    
    # Construct full URL
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{url}?{param_str}"
    print(f"Full URL: {full_url}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Sending GET request...")
            async with session.get(url, params=params, timeout=30) as response:
                status = response.status
                text = await response.text()
                
                print(f"📥 Response Status: {status}")
                print(f"📄 Response Body:")
                print("-" * 70)
                print(text[:500])
                print("-" * 70)
                
                if status == 200:
                    print("\n✅ SUCCESS! roll.wiki accepted the submission")
                else:
                    print(f"\n❌ FAILED with status {status}")
                    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_rollwiki())
