from .search import search
from .channel_info import get_channel_info

def channel_search(q, max_results = 20, order = 'relevance', previous_response = None):
    """
    Function to return the channel ids associated with the videos that match the search query.
    max_results: default 20. int value from 1 - 50
    order: default 'relevance'.  Other options are 'date', 'rating', 'viewCount', and 'title'
    previous_response: variable to allow pagination.  In order to get the next page of values, pass back the previous_response value with the same query variables
    """
    # TODO when previous_page is note None, only return channel ids that were not returned in previous search requests.
    
    response = search(q = q, part = 'snippet', type = 'video', order = order, maxResults = max_results, previous_response = previous_response)
    # extract channel ids associated with each video and remove duplicate channel ids without changing order
    channel_ids = [x['snippet']['channelId'] for x in response['items']]
    channel_ids = list(dict.fromkeys(channel_ids))
    
    channels = get_channel_info(channel_ids)
    
    return {'related_channels' : channels}
# TODO include previous response for search to add pagination (requires post instead of get)
            # 'previous_response' : response}