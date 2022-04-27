from numpy import mean
import re


def extract_emails_and_urls(description_text):
    """
    Function to extract the emails and urls from the description of a channel
    """
    email_regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'

    url_regex = r'(http|ftp|https)(://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&\/~+#-])'

    email = re.findall(email_regex, description_text)

    url = re.findall(url_regex, description_text)
    url = ["".join(x) for x in url]

    return {
                'emails'  : email,
                'urls'     : url
                }

def calculate_means(videos):
    """
    video_stats: dictionary where each key is a video_id and each value
    is a dictionary of statistics including viewCount, commentCount, and likeCount

    Returns a dictionary with the mean of all counts as values.
    """

    def calculate_mean(videos, stat):
        mean_stat =  mean([int(x['statistics'][stat]) for x in videos if stat in x['statistics']])
        return round(mean_stat)

    stat_labels = list(videos[0]['statistics'].keys())
    stats = dict()
    for label in stat_labels:
        stats[label] = calculate_mean(videos, label)
        
    return stats