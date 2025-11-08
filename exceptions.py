"""Custom exceptions for the agent"""


class TTSQuotaExceeded(Exception):
    """Raised when TTS API quota is exceeded"""
    def __init__(self, retry_after_seconds: int = 300):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"TTS quota exceeded. Retry after {retry_after_seconds} seconds.")
