from pydantic import BaseSettings

class Settings(BaseSettings):
    youtube_key: str
    token: str
    
    class Config:
        env_file = '.env'
    
