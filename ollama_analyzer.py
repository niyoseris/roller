"""
Ollama LLM Analyzer
Uses locally installed Ollama models for intelligent trend analysis
"""

import logging
import aiohttp
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

CATEGORIES = [
    "Architecture", "Arts", "Business", "Culture", "Dance", "Economics",
    "Education", "Engineering", "Entertainment", "Environment", "Fashion",
    "Film", "Food", "Geography", "History", "Literature", "Medicine",
    "Music", "Philosophy", "Politics", "Psychology", "Religion", "Science",
    "Sports", "Technology", "Theater", "Transportation"
]


class OllamaAnalyzer:
    """Ollama-powered analyzer for intelligent trend analysis"""
    
    def __init__(self, model_name: str = None):
        """Initialize Ollama analyzer"""
        self.model_name = model_name
        self.base_url = OLLAMA_BASE_URL
        if model_name:
            logger.info(f"Ollama analyzer initialized with model: {model_name}")
        else:
            logger.info("Ollama analyzer initialized (model will be auto-detected)")
    
    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    async def list_models(self) -> List[Dict]:
        """List available Ollama models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        logger.info(f"Found {len(models)} Ollama models")
                        return models
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
        return []
    
    def set_model(self, model_name: str):
        """Change the active model"""
        self.model_name = model_name
        logger.info(f"Switched to Ollama model: {model_name}")
    
    async def _generate(self, prompt: str, max_tokens: int = 100) -> Optional[str]:
        """Generate response from Ollama"""
        # Auto-detect first model if not set
        if not self.model_name:
            models = await self.list_models()
            if models:
                self.model_name = models[0]['name']
                logger.info(f"Auto-selected first available model: {self.model_name}")
            else:
                logger.error("No Ollama models available")
                return None
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '').strip()
                    else:
                        logger.error(f"Ollama request failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return None
    
    async def categorize_trend(self, trend: str, wikipedia_summary: str = "") -> str:
        """
        Use Ollama to intelligently categorize a trend
        
        Args:
            trend: The trending topic
            wikipedia_summary: Optional Wikipedia article summary for context
            
        Returns:
            Category name from the predefined list
        """
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
            response = await self._generate(prompt, max_tokens=50)
            
            if not response:
                logger.warning("Ollama returned no response")
                return "Culture"
            
            # Extract category from response
            category = response.strip().split('\n')[0].strip()
            
            # Validate category
            if category in CATEGORIES:
                logger.info(f"Ollama categorized '{trend[:50]}...' as: {category}")
                return category
            else:
                # Try to find a close match
                category_lower = category.lower()
                for valid_cat in CATEGORIES:
                    if valid_cat.lower() == category_lower:
                        logger.info(f"Ollama categorized '{trend[:50]}...' as: {valid_cat} (corrected case)")
                        return valid_cat
                
                logger.warning(f"Ollama returned invalid category '{category}', using Culture")
                return "Culture"
                
        except Exception as e:
            logger.error(f"Error in Ollama categorization: {e}")
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

            response = await self._generate(prompt, max_tokens=10)
            
            if not response:
                return 0.5  # Default medium relevance
            
            # Extract number from response
            score_text = response.strip().split()[0]
            score = float(score_text)
            
            # Clamp between 0 and 1
            score = max(0.0, min(1.0, score))
            
            logger.info(f"Ollama scored '{trend[:50]}...' with relevance: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"Error in Ollama relevance scoring: {e}")
            return 0.5  # Default medium relevance
    
    async def analyze_trend_batch(self, trends: List[str], max_concurrent: int = 3) -> List[Dict]:
        """
        Analyze multiple trends with concurrency control to avoid overwhelming Ollama
        
        Args:
            trends: List of trending topics
            max_concurrent: Maximum concurrent requests (default: 3 for local Ollama)
            
        Returns:
            List of dicts with trend analysis results
        """
        import asyncio
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def score_with_limit(trend):
            async with semaphore:
                relevance_score = await self.score_trend_relevance(trend)
                return {
                    'trend': trend,
                    'relevance_score': relevance_score
                }
        
        # Process trends with concurrency limit
        tasks = [score_with_limit(trend) for trend in trends]
        results = await asyncio.gather(*tasks)
        
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
        if not candidate_articles:
            return None
        
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

            response = await self._generate(prompt, max_tokens=100)
            
            if not response:
                return candidate_articles[0]
            
            best_match = response.strip()
            
            # Check if the response matches one of the candidates
            for article in candidate_articles:
                if article in best_match or best_match in article:
                    logger.info(f"Ollama selected '{article}' for trend '{trend[:50]}...'")
                    return article
            
            # Default to first candidate
            return candidate_articles[0]
            
        except Exception as e:
            logger.error(f"Error in Wikipedia matching: {e}")
            return candidate_articles[0] if candidate_articles else None
