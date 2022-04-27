from fastapi import FastAPI, Header, Request, status
from fastapi.responses import JSONResponse
from typing import Optional

from app.youtube.channel_info import get_channel_info
from app.youtube.channel_search import channel_search
from app.youtube.search import search
from app.youtube.video import get_video
from app.youtube.channel_demographics import get_channel_demographics
from .youtube import config

settings = config.Settings()
TOKEN = settings.token

app = FastAPI(title = "YouTubeAPI")

# @app.middleware("http")
# async def check_header_token(request: Request, call_next):
#     token = request.headers.get('token')
#     url = str(request.url) 
    
#     # check if token is included in url
#     if token != TOKEN:
#         # check if trying to access docs or redoc page
#         if '/docs' in url or '/openapi.json' in url or '/redoc' in url:
#             pass
#         else:
#             # Token incorrect, return 403 error
#             print('Token is incorrect or missing')
#             return JSONResponse(status_code=403,
#                             content = {
#                                 'code' : status.HTTP_403_FORBIDDEN,
#                                 'detail': "incorrect token"}
#                             )
#     # Token is correct or trying to access docs page, pass request on to path
#     response = await call_next(request)
#     return response


@app.get("/youtube/channels/{channel_id}")
def channel_info(
                channel_id: str,
                maxResults: Optional[int] = 20,
                return_video_stats: Optional[bool] = False,
                token: str = Header(None)
                ):

    return {
        "channel_info": get_channel_info(
                channel_id,
                maxResults = maxResults,
                return_video_stats = return_video_stats
                )
            }


@app.get("/youtube/channels/")
def search_channels(
                q: Optional[str] = None,
                max_results: Optional[int] = 20,
                order: Optional[str] = 'relevance',
                token: str = Header(None)
                ):

    if q:
        return channel_search(
                q = q,
                max_results = max_results,
                order = order)
    else:
        return None


@app.get("/youtube/channel_videos/{channel_id}")
def get_channel_videos(
                channel_id: str,
                maxResults: Optional[int] = 20,
                order: Optional[str] = 'date',
                token: str = Header(None)
                ):

    return search(
                part = 'snippet',
                channelId = channel_id,
                maxResults = maxResults,
                order = order
                )


@app.get("/youtube/videos/{video_id}")
def video_show(
                video_id: str,
                token: str = Header(None)
                ):

    return get_video(
                video_id = video_id
                )


@app.get('/youtube/channels/{channel_id}/demographics')
def channel_demographics(
                channel_id: str,
                num_videos_to_analyze: Optional[int] = 25,
                num_images_to_analyze: Optional[int] = 300,
                token: str = Header(None)
                ):

    return get_channel_demographics(
                channel_id = channel_id,
                num_videos_to_analyze = num_videos_to_analyze,
                num_images_to_analyze = num_images_to_analyze)



