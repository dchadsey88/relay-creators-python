import pandas as pd
from collections import Counter
import numpy as np
import requests

from googleapiclient.discovery import build
from . import config

settings = config.Settings()
KEY = settings.youtube_key


youtube = build('youtube', 'v3', developerKey= KEY)

def get_channel_videos(channel_id, num_videos_to_analyze) -> list():

    # exchange channel_id UC with UU to create the channel playlist id
    playlist_id = channel_id[0] + 'U' + channel_id[2:]

    playlistItems = youtube.playlistItems()
    request = playlistItems.list(playlistId = playlist_id, part = 'contentDetails', maxResults = 50)

    channel_video_ids = list()

    # get channel videos until total videos >= num_videos
    while num_videos_to_analyze > len(channel_video_ids):

        # execute request and extract video ids
        response = request.execute()
        channel_video_ids.extend([x['contentDetails']['videoId']  for x in response['items']])

        # set next request for next page
        request = playlistItems.list_next(request, response)

        # check to see if there are no more videos
        if not request:
            print('no more videos')
            break

    return channel_video_ids[:num_videos_to_analyze]


def get_commentor_channel_ids(channel_video_ids):
    #TODO if total number of comments is less than X and sonme responses have 100 comments, store response and call client again until sufficient comments
    channel_comments = list()
    # reply_counts = list() # removed this as it was not being used

    def extract_comments(request_id, response, exception):
        if exception is not None:
            pass
        else:
            channel_comments.extend([x['snippet']['topLevelComment']['snippet'] for x in response['items']])

    batch = youtube.new_batch_http_request(callback = extract_comments)

    for video_id in channel_video_ids:
        batch.add(youtube.commentThreads().list(videoId = video_id,
                                                order = 'relevance',
                                                part = 'snippet',
                                                maxResults = 100))
    batch.execute()
    
    channel_comments_df = pd.DataFrame(channel_comments)
    
    # edge case for when comments are disabled on a video
    if not channel_comments_df.empty:
        # Unnest authorChannelId from a list to a string
        channel_comments_df['authorChannelId'] = channel_comments_df['authorChannelId'].apply(lambda x: x['value'] if not pd.isna(x) else '')
        commentor_channel_ids = channel_comments_df['authorChannelId'].values.tolist()
        commentor_channel_ids = list(set(commentor_channel_ids))
        return commentor_channel_ids
    else:
        return list()

def get_channel_snippets(channel_id_list):
    channel_snippet_list = list()
    def extract_countries(request_id, response, exception):
        if exception is not None:
            pass
        else:
            # if 'items' in response.keys():
                # countries.extend([x['snippet']['country'] for x in response['items'] if 'country' in x['snippet'].keys()])
            channel_snippet_list.append(response['items'])
            
    batch = youtube.new_batch_http_request(callback = extract_countries)

    for i in range((len(channel_id_list) // 50) +1):
        channel_str = ",".join(channel_id_list[50*i:50*i + 50])
        batch.add(youtube.channels().list(id = channel_str,
                                            part = 'snippet'))
    batch.execute()

    # unnest elements
    channel_snippet_list = [x for sublist in channel_snippet_list for x in sublist]
    
    return channel_snippet_list

def get_channel_demographics(channel_id, num_videos_to_analyze = 25, num_images_to_analyze = 20):
    # get the most recent videos from the channel
    channel_video_ids = get_channel_videos(channel_id = channel_id,
            num_videos_to_analyze = num_videos_to_analyze)
    
    # get a list of unique commentor_channel_ids looking at the first 100 comments of each video.  If comments disabled, returns an empty list.
    commentor_channel_ids = get_commentor_channel_ids(channel_video_ids)

    if len(commentor_channel_ids) != 0:
        
        # get the channel snippet for each commentor channel id
        channel_snippet_list = get_channel_snippets(commentor_channel_ids)

        # calculate countries_dict
        countries = [x['snippet']['country'] for x in channel_snippet_list if 'country' in x['snippet']]
        country_dict = Counter(countries)
        total_countries = sum(country_dict.values())
        for key in country_dict:
            country_dict[key] = round((country_dict[key] /total_countries) * 100, 2) 
        country_dict = {k:v for k, v in sorted(country_dict.items(), key = lambda x: -x[1])}
        
        # Create a dictionary of channel_id, img_url key-value pairs to pass through deepface
        id_img_dict = [(x['id'], x['snippet']['thumbnails']['medium']['url']) for x in channel_snippet_list]
        # Truncate list to num_images_to_analyze
        
        # id_img_dict = dict(id_img_dict[:num_images_to_analyze])
        id_img_dict = dict(id_img_dict[:20]) # Currently cap to 20 images
        # send img urls to deepface api
        print('connecting to deepface-ai...')
        local_url = "http://localhost:8000/predict"
        api_url = 'https://relay-deep-face-ai.relay.club/predict/'
        headers = {"Content-Type" : 'application/json; charset=utf-8'}
        request = requests.post(local_url, 
                                 json ={'images': id_img_dict}, 
                                 headers = headers)
       
        print(request.status_code)
        
        response = request.json()
        
        # Aggregate age from response and generate age_dict
        age_list = [x['age'] for x in response['predictions'].values() if x['age'] is not None]
        # If there are no faces, return an empty dictionary, else create a histogram of ages
        if len(age_list) > 0:
            age_bins = ['13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65']
            age_hist_values, _ = np.histogram(age_list, bins = [0, 17, 24, 34, 44, 54, 64])
            age_dict = dict()
            total_ages = sum(age_hist_values)
            for age_bin, v in zip(age_bins, age_hist_values):
                age_dict[age_bin] = round(v/total_ages * 100, 2)
        else:
            age_dict = {}
        
        # Aggregate from response and generate gender_dict
        genders = [x['gender'] for x in response['predictions'].values() if x['gender'] is not None]
        gender_dict = Counter(genders)
        total_genders = len(genders)
        for key in gender_dict:
            gender_dict[key] = round(gender_dict[key]/total_genders *100 , 2)
        gender_dict = dict(gender_dict)
        
        result =  {
            'channel_id' : channel_id,
            'country_demographics': country_dict,
            'age_demographics' : age_dict,
            'gender_demographics' : gender_dict,
            'comments_disabled' : False}
    else:
        result = {
            'channel_id' : channel_id,
            'comments_disabled' : False}

    return result