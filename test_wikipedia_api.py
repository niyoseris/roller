"""
Direct Wikipedia API test
"""
import asyncio
import aiohttp
import json

async def test_api():
    """Test Wikipedia API directly"""
    
    url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': '1',
        'explaintext': '1',
        'titles': 'NBA',
        'format': 'json'
    }
    
    print("🧪 Testing Wikipedia API directly")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                print(f"\nPage ID: {page_id}")
                if page_id != '-1':
                    extract = page_data.get('extract', '')
                    print(f"Extract: {extract[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_api())
