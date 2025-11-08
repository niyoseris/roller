"""
Twitter Browser Poster - Posts tweets using browser automation
Handles authentication and posting via Selenium
"""

import logging
import time
import os
from typing import Optional
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TwitterBrowserPoster:
    """Handles posting to Twitter using browser automation"""
    
    def __init__(self, username: str = None, password: str = None, email: str = None):
        """
        Initialize Twitter browser poster
        
        Args:
            username: Twitter username or handle
            password: Twitter password
            email: Twitter email (for verification if needed)
        """
        self.username = username or os.getenv('TWITTER_USERNAME')
        self.password = password or os.getenv('TWITTER_PASSWORD')
        self.email = email or os.getenv('TWITTER_EMAIL')
        self.driver = None
        self.is_logged_in = False
        self.enabled = False
        
        # Check if credentials are available
        if not all([self.username, self.password]):
            logger.warning("Twitter credentials not configured. Twitter posting disabled.")
            logger.info("To enable Twitter posting, set these environment variables:")
            logger.info("  - TWITTER_USERNAME")
            logger.info("  - TWITTER_PASSWORD")
            logger.info("  - TWITTER_EMAIL (optional, for verification)")
            return
        
        self.enabled = True
        logger.info("✅ Twitter browser poster initialized")
    
    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add user agent to avoid bot detection
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            
            logger.info("✅ Chrome WebDriver initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {e}")
            return False
    
    def _login(self) -> bool:
        """Login to Twitter"""
        try:
            logger.info("🔐 Logging into Twitter...")
            
            # Navigate to Twitter login
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(3)
            
            # Enter username
            logger.info("  → Entering username...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(self.username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Check if email verification is needed
            try:
                email_input = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if email_input and self.email:
                    logger.info("  → Email verification required, entering email...")
                    email_input.send_keys(self.email)
                    email_input.send_keys(Keys.RETURN)
                    time.sleep(2)
            except NoSuchElementException:
                pass
            
            # Enter password
            logger.info("  → Entering password...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Check if login was successful
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]'))
                )
                self.is_logged_in = True
                logger.info("✅ Successfully logged into Twitter!")
                return True
            except TimeoutException:
                logger.error("❌ Login failed - could not find home button")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def _post_tweet_internal(self, tweet_text: str) -> bool:
        """Post a tweet (internal method)"""
        try:
            # Click on tweet compose button
            logger.info("  → Opening tweet compose...")
            compose_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="SideNav_NewTweet_Button"]'))
            )
            compose_button.click()
            time.sleep(2)
            
            # Enter tweet text
            logger.info("  → Entering tweet text...")
            tweet_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="tweetTextarea_0"]'))
            )
            tweet_input.send_keys(tweet_text)
            time.sleep(1)
            
            # Click post button
            logger.info("  → Posting tweet...")
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="tweetButtonInline"]'))
            )
            post_button.click()
            time.sleep(3)
            
            logger.info("✅ Tweet posted successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error posting tweet: {e}")
            return False
    
    def post_tweet(self, trend: str, category: str, article_id: Optional[int]) -> bool:
        """
        Post a tweet about the article
        
        Args:
            trend: The trending topic
            category: The article category
            article_id: The roll.wiki article ID
            
        Returns:
            True if tweet was posted successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Twitter posting is disabled - skipping tweet")
            return False
        
        if not article_id:
            logger.warning("No article_id provided - cannot post tweet")
            return False
        
        try:
            # Initialize driver if not already done
            if not self.driver:
                if not self._init_driver():
                    return False
            
            # Login if not already logged in
            if not self.is_logged_in:
                if not self._login():
                    return False
            
            # Format tweet
            roll_wiki_url = f"https://roll.wiki/summary/{article_id}"
            
            # Clean trend name
            import re
            clean_trend = re.sub(r'\d+[KkMm]?\s*$', '', trend).strip()
            clean_trend = clean_trend.lstrip('#')
            
            tweet_text = f"📰 {clean_trend} - {category}\n🔗 {roll_wiki_url}\n#Wikipedia #Trending"
            
            # Post tweet
            logger.info(f"🐦 Posting tweet: {tweet_text[:50]}...")
            return self._post_tweet_internal(tweet_text)
            
        except Exception as e:
            logger.error(f"❌ Error in post_tweet: {e}")
            return False
    
    async def post_tweet_async(self, trend: str, category: str, article_id: Optional[int]) -> bool:
        """
        Async wrapper for post_tweet
        
        Args:
            trend: The trending topic
            category: The article category
            article_id: The roll.wiki article ID
            
        Returns:
            True if tweet was posted successfully, False otherwise
        """
        import asyncio
        return await asyncio.to_thread(self.post_tweet, trend, category, article_id)
    
    def is_enabled(self) -> bool:
        """Check if Twitter posting is enabled"""
        return self.enabled
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
