"""
Test Wikipedia summary fetching
"""
import asyncio
import logging
from wikipedia_finder import WikipediaFinder

# Enable logging
logging.basicConfig(level=logging.DEBUG)

async def test_summary():
    """Test Wikipedia summary API"""
    finder = WikipediaFinder()
    
    test_cases = [
        "NBA",
        "Donald Trump",
        "Ukraine",
        "Micah",
        "Taylor Swift"
    ]
    
    print("🧪 Testing Wikipedia Summary API")
    print("=" * 70)
    
    for title in test_cases:
        print(f"\n📌 Title: {title}")
        print("-" * 70)
        
        summary = await finder.get_summary_by_title(title)
        
        if summary:
            print(f"✅ Summary found ({len(summary)} chars):")
            print(f"{summary}")
        else:
            print(f"❌ No summary found")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_summary())
