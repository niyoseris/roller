"""
Test content filtering for meaningless pages
"""

import asyncio
from wikipedia_finder import WikipediaFinder

async def test_filtering():
    """Test filtering of different page types"""
    
    finder = WikipediaFinder()
    
    print("=" * 70)
    print("Testing Content Filtering")
    print("=" * 70)
    
    # Test cases with expected results
    test_cases = [
        ("Smith (surname)", "surname page - should skip"),
        ("John (given name)", "given name page - should skip"),
        ("Mercury", "disambiguation - should skip"),
        ("List of countries", "list page - should skip"),
        ("Python (programming language)", "real article - should process"),
        ("Albert Einstein", "real article - should process"),
    ]
    
    for title, description in test_cases:
        print(f"\n{'='*70}")
        print(f"📌 Testing: {title}")
        print(f"   Expected: {description}")
        print('='*70)
        
        summary = await finder.get_summary_by_title(title)
        
        if not summary:
            print(f"❌ No Wikipedia article found")
            continue
        
        print(f"Summary: {summary[:150]}...")
        
        summary_lower = summary.lower()
        
        # Test filters
        skip_reasons = []
        
        # 1. Disambiguation
        disambiguation_indicators = [
            "may refer to:", "may refer to", "may mean:", "may stand for:",
            "can refer to:", "most commonly refers to:", "commonly refers to:",
            "disambiguation", "is a disambiguation"
        ]
        if any(ind in summary_lower for ind in disambiguation_indicators):
            skip_reasons.append("Disambiguation")
        
        # 2. Name/Surname
        name_indicators = [
            "is a surname", "is a family name", "is a given name",
            "is a masculine given name", "is a feminine given name",
            "is a common surname", "is an english surname", "is a name",
            "as a surname", "as a given name"
        ]
        if any(ind in summary_lower for ind in name_indicators):
            skip_reasons.append("Name/Surname")
        
        # 3. List pages
        if summary_lower.startswith("this is a list of") or summary_lower.startswith("list of"):
            skip_reasons.append("List page")
        
        # 4. Short content
        if len(summary) < 100:
            skip_reasons.append(f"Too short ({len(summary)} chars)")
        
        if skip_reasons:
            print(f"⏭️  SKIP: {', '.join(skip_reasons)}")
        else:
            print(f"✅ PROCESS: Good content ({len(summary)} chars)")

if __name__ == "__main__":
    asyncio.run(test_filtering())
