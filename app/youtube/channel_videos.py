from googleapiclient.discovery import build

from .search import search
from . import config

settings = config.Settings()
KEY = settings.youtube_key

youtube = build('youtube', 'v3', developerKey= KEY)

def get_channel_recent_videos(channel_id, max_results, part):
    
    # adjust channelId into platlistId
    playlist_id = channel_id[0] + 'U' + channel_id[2:]
    
    # instantiate api client and request
    youtube = build('youtube', 'v3', developerKey= KEY)
    playlistItems = youtube.playlistItems()
    request = playlistItems.list(playlistId = playlist_id, part = part, maxResults = 50)
        
    channel_vidoes = list()
    # get channel videos until total videos >= max_results
    while max_results > len(channel_vidoes):
        
        # execute request and extract video ids
        response = request.execute()
        channel_vidoes.extend(response['items'])
        # video_ids.extend([x['contentDetails']['videoId']  for x in response['items']])

        # set next request for next page
        request = playlistItems.list_next(request, response)

        # check to see if there are no more videos
        if not request:
            break
        
    return channel_vidoes[:max_results]

def get_channel_videos(channel_id,
                       order = 'date', 
                       max_results = 20,
                       part = 'snippet'):
    """
    Function to get the videos for a specified channel.
    Channel_id: 24 character str starting with UC containing the channel id
    
    order: order in which videos are returned.  Defaul is date (most recent first) 
    which uses 1 credit.
    Other accepted values are rating, relevance, title (alphabetically) which use the 
    search function and 100 credits per call
    
    max_results: default value is 20.  Max value is 50 unless order = 'date' which will allow
    pagination and can collect all video ids
    """
    # get all video ids for a channel
    # if order is date, use playlistItems function, otherwise call search function
    if order == 'date':
        channel_vidoes = get_channel_recent_videos(channel_id = channel_id, max_results = max_results, part = part)
        video_ids = [x['snippet']['resourceId']['videoId'] for x in channel_vidoes]
        
    else:
        #TODO add paginiation ability to collect more than 50 results
        response = search(channelId = channel_id,
                                        order = order,
                                        maxResults = max_results,
                                        part = part,
                                        type = 'video')
 
        channel_vidoes = response['items']
        video_ids = [x['id']['videoId'] for x in channel_vidoes]
    
    # use videos endpoint to get the snippet and stats for videos in video_ids
    request = youtube.videos().list(part = 'snippet,statistics',id = video_ids)
    response = request.execute()
    
    # return just the items which contains a list of dictionaries, one for each video
    videos = response['items']
    
    # Remove 'kind' and 'etag' keys from each item in list
    videos = [{k:v for k, v in video.items() if k != 'etag' and k!= 'kind'} for video in videos]
    
    return videos


