"""
LLM Analyzer using Gemini 2.0 Flash
Provides intelligent analysis for trend categorization and relevance scoring
"""

import logging
import google.generativeai as genai
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyB_3b_pGtqDs5BDI5f57KTsxp2L8LHnGfQ"
GEMINI_MODEL = "gemini-2.0-flash-exp"

CATEGORIES = [
    "Architecture", "Arts", "Business", "Culture", "Dance", "Economics",
    "Education", "Engineering", "Entertainment", "Environment", "Fashion",
    "Film", "Food", "Geography", "History", "Literature", "Medicine",
    "Music", "Philosophy", "Politics", "Psychology", "Religion", "Science",
    "Sports", "Technology", "Theater", "Transportation"
]


class GeminiAnalyzer:
    """Gemini-powered analyzer for intelligent trend analysis"""
    
    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Gemini analyzer"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            logger.info(f"Gemini analyzer initialized with model: {GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.model is not None
    
    async def categorize_trend(self, trend: str, wikipedia_summary: str = "") -> str:
        """
        Use Gemini to intelligently categorize a trend
        
        Args:
            trend: The trending topic
            wikipedia_summary: Optional Wikipedia article summary for context
            
        Returns:
            Category name from the predefined list
        """
        if not self.is_available():
            logger.warning("Gemini not available, using fallback categorization")
            return "Culture"
        
        try:
            # Prepare prompt
            prompt = f"""Analyze the following trending topic and categorize it into ONE category.

Trending Topic: {trend}

{f"Wikipedia Summary: {wikipedia_summary[:500]}" if wikipedia_summary else ""}

Available Categories (MUST choose ONE):
{", ".join(CATEGORIES)}

Instructions:
1. Analyze the topic and its context carefully
2. Choose the MOST appropriate category from the list above
3. Respond with ONLY the category name, nothing else
4. The category name MUST be exactly as listed (case-sensitive)

Category:"""

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "max_output_tokens": 50,
                }
            )
            
            category = response.text.strip()
            
            # Validate category
            if category in CATEGORIES:
                logger.info(f"Gemini categorized '{trend[:50]}...' as: {category}")
                return category
            else:
                # Try to find a close match
                category_lower = category.lower()
                for valid_cat in CATEGORIES:
                    if valid_cat.lower() == category_lower:
                        logger.info(f"Gemini categorized '{trend[:50]}...' as: {valid_cat} (corrected case)")
                        return valid_cat
                
                logger.warning(f"Gemini returned invalid category '{category}', using Culture")
                return "Culture"
                
        except Exception as e:
            logger.error(f"Error in Gemini categorization: {e}")
            return "Culture"
    
    async def score_trend_relevance(self, trend: str) -> float:
        """
        Score how relevant/important a trend is (0.0 to 1.0)
        Higher scores indicate more significant/newsworthy trends
        
        Args:
            trend: The trending topic
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not self.is_available():
            return 0.5  # Default medium relevance
        
        try:
            prompt = f"""Analyze the following trending topic and rate its relevance/importance.

Trending Topic: {trend}

Instructions:
1. Consider factors like: newsworthiness, cultural significance, public interest, educational value
2. Rate on a scale of 0.0 to 1.0 where:
   - 0.0-0.3: Low relevance (spam, trivial, unclear)
   - 0.4-0.6: Medium relevance (somewhat interesting)
   - 0.7-1.0: High relevance (important news, significant events, educational)
3. Respond with ONLY a number between 0.0 and 1.0

Relevance Score:"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 10,
                }
            )
            
            score_text = response.text.strip()
            score = float(score_text)
            
            # Clamp between 0 and 1
            score = max(0.0, min(1.0, score))
            
            logger.info(f"Gemini scored '{trend[:50]}...' with relevance: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"Error in Gemini relevance scoring: {e}")
            return 0.5  # Default medium relevance
    
    async def analyze_trend_batch(self, trends: List[str]) -> List[Dict]:
        """
        Analyze multiple trends in batch for efficiency
        
        Args:
            trends: List of trending topics
            
        Returns:
            List of dicts with trend analysis results
        """
        results = []
        
        for trend in trends:
            relevance_score = await self.score_trend_relevance(trend)
            results.append({
                'trend': trend,
                'relevance_score': relevance_score
            })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results
    
    async def find_best_wikipedia_match(self, trend: str, candidate_articles: List[str]) -> Optional[str]:
        """
        Given multiple Wikipedia article candidates, find the best match
        
        Args:
            trend: The trending topic
            candidate_articles: List of Wikipedia article titles
            
        Returns:
            Best matching article title or None
        """
        if not self.is_available() or not candidate_articles:
            return candidate_articles[0] if candidate_articles else None
        
        try:
            prompt = f"""Given a trending topic and several Wikipedia article candidates, choose the MOST relevant article.

Trending Topic: {trend}

Article Candidates:
{chr(10).join(f"{i+1}. {article}" for i, article in enumerate(candidate_articles))}

Instructions:
1. Choose the article that best matches the trending topic
2. Respond with ONLY the exact article title from the list above
3. If none match well, respond with the first article

Best Match:"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 100,
                }
            )
            
            best_match = response.text.strip()
            
            # Check if the response matches one of the candidates
            for article in candidate_articles:
                if article in best_match or best_match in article:
                    logger.info(f"Gemini selected '{article}' for trend '{trend[:50]}...'")
                    return article
            
            # Default to first candidate
            return candidate_articles[0]
            
        except Exception as e:
            logger.error(f"Error in Wikipedia matching: {e}")
            return candidate_articles[0] if candidate_articles else None
