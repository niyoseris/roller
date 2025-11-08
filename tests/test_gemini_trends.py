"""Test Gemini Wikipedia finder"""
import asyncio
from gemini_analyzer import GeminiAnalyzer

async def test():
    analyzer = GeminiAnalyzer()
    
    # Check availability
    available = await analyzer.is_available()
    print(f"🔍 Gemini API Available: {available}")
    
    if not available:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    # Test with sample trends
    trends = ["NBA", "Apple", "Tesla"]
    print(f"\n📋 Testing with trends: {trends}")
    print("⏳ Calling Gemini...")
    
    try:
        result = await analyzer.find_wikipedia_pages_for_trends(trends)
        
        if result:
            print(f"\n✅ Success! Found {len(result)} results:")
            for trend, data in result.items():
                if isinstance(data, dict):
                    print(f"  - {trend}:")
                    print(f"      URL: {data.get('url')}")
                    print(f"      Category: {data.get('category')}")
                else:
                    print(f"  - {trend}: {data}")
        else:
            print("\n❌ No results returned (empty dict)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test())
