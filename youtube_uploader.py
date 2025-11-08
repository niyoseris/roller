"""
YouTube Video Uploader
Automatically uploads videos to YouTube with metadata
"""

import os
import logging
import pickle
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Upload videos to YouTube"""
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file='youtube_credentials.json'):
        """
        Initialize YouTube uploader
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
                             Get from: https://console.cloud.google.com/apis/credentials
        """
        self.credentials_file = credentials_file
        self.token_file = 'youtube_token.pickle'
        self.youtube = None
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API
        
        Returns:
            True if authentication successful
        """
        try:
            creds = None
            
            # Load saved credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing YouTube credentials...")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.error("Please download OAuth2 credentials from Google Cloud Console")
                        return False
                    
                    logger.info("Starting YouTube OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=8080)
                
                # Save credentials
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build YouTube API client
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.authenticated = True
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",  # public, private, or unlisted
        is_shorts: bool = True  # Upload as YouTube Shorts
    ) -> Optional[str]:
        """
        Upload video to YouTube (optimized for Shorts)
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags (max 500 chars total)
            category_id: YouTube category ID
            privacy_status: Privacy setting
            is_shorts: Upload as YouTube Shorts (adds #Shorts tag)
        
        Returns:
            Video ID if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated with YouTube")
            if not self.authenticate():
                return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        try:
            # Add #Shorts hashtag for Shorts videos
            final_description = description
            if is_shorts:
                if '#Shorts' not in description and '#shorts' not in description:
                    final_description = f"{description}\n\n#Shorts"
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube limit
                    'description': final_description[:5000],  # YouTube limit
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Prepare media file
            media = MediaFileUpload(
                video_path,
                mimetype='video/*',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # Execute upload
            logger.info(f"Uploading video to YouTube: {title}")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Video uploaded successfully!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            return video_id
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def update_video(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: list = None
    ) -> bool:
        """
        Update video metadata
        
        Args:
            video_id: YouTube video ID
            title: New title
            description: New description
            tags: New tags
        
        Returns:
            True if successful
        """
        if not self.authenticated:
            if not self.authenticate():
                return False
        
        try:
            # Get current video details
            video = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video['items']:
                logger.error(f"Video not found: {video_id}")
                return False
            
            snippet = video['items'][0]['snippet']
            
            # Update only provided fields
            if title:
                snippet['title'] = title[:100]
            if description:
                snippet['description'] = description[:5000]
            if tags:
                snippet['tags'] = tags
            
            # Update video
            self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            logger.info(f"Video metadata updated: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating video: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with YouTube"""
        return self.authenticated


# Test function
def test_uploader():
    """Test YouTube uploader"""
    uploader = YouTubeUploader()
    
    print("Testing YouTube authentication...")
    if uploader.authenticate():
        print("✅ Authentication successful!")
        print("\nTo upload a video, call:")
        print('uploader.upload_video("video.mp4", "My Title", "Description", ["tag1", "tag2"])')
    else:
        print("❌ Authentication failed")
        print("\nSetup instructions:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download JSON and save as 'youtube_credentials.json'")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_uploader()
