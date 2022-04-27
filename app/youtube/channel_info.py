from googleapiclient.discovery import build

from .utils import calculate_means, extract_emails_and_urls
from .channel_videos import get_channel_videos
from . import config

settings = config.Settings()
KEY = settings.youtube_key


def get_channel_info(
                    channel_ids_str,
                    maxResults = 20,
                    return_video_stats = False,
                    part = 'snippet,statistics,topicDetails,brandingSettings'
                    ):
        """
        Function to get channel info
        Channel_ids: List of one or more ids or a string of comma seperated ids
        """
        youtube = build('youtube', 'v3', developerKey= KEY)
        # request channel info from google api
        request = youtube.channels().list(part = part, id = channel_ids_str)
        response = request.execute()
        
        channel_info_list = response['items']
        
        # Extract any email(s) and/or url(s) from the description text
        for channel in channel_info_list:
                channel['contactInfo'] = extract_emails_and_urls(channel['snippet']['description'])

        if return_video_stats:
                # Use only the first channel id if there is more than one
                if type(channel_ids_str) == list:
                        channel_id = channel_ids_str[0]
                elif type(channel_ids_str) == str:
                        channel_id = channel_ids_str.split(',',1)[0]
                        
                most_recent_videos = get_channel_videos(
                                        channel_id=channel_id,
                                        order = 'date',
                                        max_results= maxResults
                                        )
                most_recent_videos_stats = calculate_means(most_recent_videos)
                
                channel_info_list[0]['recent_posts'] = {'stats' : most_recent_videos_stats,
                                                        'videos': most_recent_videos}
                
                top_videos = get_channel_videos(
                                        channel_id=channel_id,
                                        order = 'viewCount',
                                        max_results= maxResults
                                        )
                top_video_stats = calculate_means(top_videos)

                channel_info_list[0]['popular_posts'] = {'stats' : top_video_stats,
                                                        'videos': top_videos}
        
        return channel_info_list