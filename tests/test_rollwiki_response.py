"""
Test roll.wiki response format to understand article_id extraction
"""

import asyncio
import aiohttp
import json

ROLL_WIKI_API = "https://roll.wiki/api/v1/summarize"
SECRET = "laylaylom"

async def test_rollwiki():
    """Test roll.wiki responses"""
    
    # Test 1: Submit an existing article to get 409 response
    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    
    print("\n📝 Note: This article likely already exists in roll.wiki")
    print("   We should get a 409 status to see its response format")
    
    params = {
        "url": test_url,
        "save": "true",
        "category": "Technology",
        "secret": SECRET
    }
    
    print("=" * 60)
    print("Testing roll.wiki API Response Format")
    print("=" * 60)
    print(f"\nSubmitting: {test_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ROLL_WIKI_API, params=params, timeout=120) as response:
                response_text = await response.text()
                status = response.status
                
                print(f"\nStatus Code: {status}")
                print(f"\nFull Response:")
                print(response_text[:500])
                print("\n" + "=" * 60)
                
                # Parse JSON
                try:
                    response_data = json.loads(response_text)
                    print("\nParsed JSON:")
                    print(json.dumps(response_data, indent=2))
                    print("\n" + "=" * 60)
                    
                    # Try different extraction methods
                    print("\nTrying different article_id extraction methods:")
                    
                    method1 = response_data.get('data', {}).get('article_id')
                    print(f"  Method 1 - response_data['data']['article_id']: {method1}")
                    
                    method2 = response_data.get('article_id')
                    print(f"  Method 2 - response_data['article_id']: {method2}")
                    
                    method3 = response_data.get('id')
                    print(f"  Method 3 - response_data['id']: {method3}")
                    
                    # Method 4: Parse from error message (for 409 responses)
                    import re
                    error_message = response_data.get('error', '')
                    if error_message:
                        print(f"  Error message: {error_message}")
                        match = re.search(r'with ID (\d+)', error_message)
                        if match:
                            method4 = int(match.group(1))
                            print(f"  Method 4 - Extracted from error message: {method4}")
                        else:
                            method4 = None
                    else:
                        method4 = None
                    
                    # Final result
                    article_id = method1 or method2 or method3 or method4
                    print(f"\n✅ Final article_id: {article_id}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_rollwiki())
