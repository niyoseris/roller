"""
Test script for LLM integration with Gemini 2.0 Flash
"""

import asyncio
from llm_analyzer import GeminiAnalyzer

async def test_llm():
    """Test Gemini LLM analyzer"""
    print("=" * 60)
    print("Testing Gemini 2.0 Flash Integration")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    
    # Check if available
    print(f"\n1. Gemini Available: {analyzer.is_available()}")
    
    if not analyzer.is_available():
        print("ERROR: Gemini not available!")
        return
    
    # Test categorization
    print("\n2. Testing Categorization...")
    test_trends = [
        "Tesla earnings report Q4 2024",
        "Lakers vs Warriors NBA game highlights",
        "Climate change summit in Paris"
    ]
    
    for trend in test_trends:
        category = await analyzer.categorize_trend(trend)
        print(f"   Trend: '{trend}'")
        print(f"   Category: {category}\n")
    
    # Test relevance scoring
    print("3. Testing Relevance Scoring...")
    test_items = [
        "Major earthquake hits California",
        "Random social media drama",
        "NASA discovers water on Mars"
    ]
    
    for item in test_items:
        score = await analyzer.score_trend_relevance(item)
        print(f"   Item: '{item}'")
        print(f"   Relevance: {score:.2f}\n")
    
    # Test batch analysis
    print("4. Testing Batch Analysis...")
    batch_trends = [
        "Presidential election results",
        "Cute cat video goes viral",
        "New cancer treatment breakthrough",
        "Celebrity gossip",
        "AI breakthrough in quantum computing"
    ]
    
    results = await analyzer.analyze_trend_batch(batch_trends)
    print("   Sorted by relevance (highest first):")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['trend'][:50]}: {result['relevance_score']:.2f}")
    
    print("\n" + "=" * 60)
    print("LLM Integration Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_llm())
