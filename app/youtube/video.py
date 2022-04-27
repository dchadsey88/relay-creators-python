from googleapiclient.discovery import build

from .utils import extract_emails_and_urls
from .channel_info import get_channel_info
from . import config

settings = config.Settings()
KEY = settings.youtube_key


def get_video(video_id):
    """
    Function to return snippet and stats for one or more videos
    id: str with one or more video ids (comma seperated)
    
    The function will return a list with 1 item per video id.  For each video,
    there will be a snippet and the video stats.
    In addition, the videos reach rate and engagement rate are calculated using the 
    channel subscriber count.
    Any urls or emails are also extracted from the video description.
    """
    # call the youtube clinet to get the video snippet and statistics
    youtube = build('youtube', 'v3', developerKey= KEY)
    request = youtube.videos().list(id = video_id, part = 'snippet,statistics')
    response = request.execute()
    
    video_list = response['items']
    
    # Get channel statistics using the channel_info get_channel_info function
    channel_ids = [x['snippet']['channelId'] for x in video_list]
    channel_info = get_channel_info(channel_ids, return_video_stats= False)
    channel_statistics = [x['statistics'] for x in channel_info]
    
    for vid, channel_stats in zip(video_list, channel_statistics):
        # extract any urls or emails from the video description
        vid['affiliatedLinks'] = extract_emails_and_urls(vid['snippet']['description'])
        
        # get the basic stats from the video and channel stats
        likeCount = int(vid['statistics']['likeCount'])
        commentCount = int(vid['statistics']['commentCount'])
        viewCount = int(vid['statistics']['viewCount'])
        subscriberCount = int(channel_stats['subscriberCount'])
        
        # calculate the video engagment rate and reach rate and append to each video stats key
        vid['videoEngagementRate'] = (likeCount + commentCount)/viewCount
        vid['reachRate'] = subscriberCount / viewCount
        
    # Reconfigure response to match frontend exptected response
    video_list = [{'video_response' : {'kind' : x['kind'],
                      'etag' : x['etag'],
                      'id' : x['id'],
                      'snippet' : x['snippet'],
                      'statistics' : x['statistics']},
                'affiliatedLinks' : x['affiliatedLinks'],
                'videoEngagementRate' : x['videoEngagementRate'],
                'reachRate' : x['reachRate']} for x in video_list]
    # return just the first item in the list
    return video_list[0]