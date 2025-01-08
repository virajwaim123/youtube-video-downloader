from pydantic import BaseModel

class YouTubeVideoURL(BaseModel):
    url: str