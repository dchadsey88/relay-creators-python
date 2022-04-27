from googleapiclient.discovery import build

from . import config

settings = config.Settings()
KEY = settings.youtube_key

def search(previous_response = None, **kwargs):
    """
    Search function.
    """
    youtube = build('youtube', 'v3', developerKey= KEY)
    
    request = youtube.search().list(**kwargs)
    
    if not previous_response:
        response = request.execute()
    else:
        request = youtube.search().list_next(previous_request = request,
                                             previous_response = previous_response)
        response = request.execute()
        
    return response