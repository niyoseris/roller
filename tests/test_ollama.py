"""
Test script for Ollama integration
"""

import asyncio
from ollama_analyzer import OllamaAnalyzer

async def test_ollama():
    """Test Ollama LLM analyzer"""
    print("=" * 60)
    print("Testing Ollama Integration")
    print("=" * 60)
    
    # Test with default model
    analyzer = OllamaAnalyzer()
    
    # Check if available
    print(f"\n1. Checking Ollama connection...")
    is_available = await analyzer.is_available()
    print(f"   Ollama Available: {is_available}")
    
    if not is_available:
        print("\n⚠️  ERROR: Ollama not available!")
        print("   Make sure Ollama is running: ollama serve")
        return
    
    # List models
    print("\n2. Listing Available Models...")
    models = await analyzer.list_models()
    if models:
        print(f"   Found {len(models)} models:")
        for model in models:
            print(f"   - {model.get('name', 'unknown')}")
    else:
        print("   No models found!")
        print("   Download a model: ollama pull llama3.2")
        return
    
    # Test categorization
    print("\n3. Testing Categorization...")
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
    print("4. Testing Relevance Scoring...")
    test_items = [
        "Major earthquake hits California",
        "Random social media drama",
        "NASA discovers water on Mars"
    ]
    
    for item in test_items:
        score = await analyzer.score_trend_relevance(item)
        print(f"   Item: '{item}'")
        print(f"   Relevance: {score:.2f}\n")
    
    # Test model switching
    print("5. Testing Model Switching...")
    if len(models) > 1:
        new_model = models[1]['name']
        print(f"   Switching to: {new_model}")
        analyzer.set_model(new_model)
        print(f"   Current model: {analyzer.model_name}")
    else:
        print("   Only one model available, skipping switch test")
    
    print("\n" + "=" * 60)
    print("Ollama Integration Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ollama())
