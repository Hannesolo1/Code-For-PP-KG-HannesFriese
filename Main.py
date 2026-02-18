import kagglehub
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# retrieve latest data
path = '/Users/hannes/Documents/University/KnowledgeGraphs/Data/dance data.csv'

# Load YouTube API key
def load_youtube_api_key():
    """Load the YouTube API key from yt_key.txt file"""
    with open('yt_key.txt', 'r') as f:
        line = f.read().strip()
        if line.startswith('key='):
            return line.split('=', 1)[1]
        return line

# Initialize YouTube API client
def get_youtube_client():
    """Create and return a YouTube API client"""
    api_key = load_youtube_api_key()
    return build('youtube', 'v3', developerKey=api_key)

# Example: Search for videos
def search_videos(youtube, query, max_results=5):
    """
    Search for videos on YouTube

    Args:
        youtube: YouTube API client
        query: Search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        List of video information dictionaries
    """
    try:
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            videoDuration='medium',  # Excludes shorts (short=<4min, medium=4-20min, long=>20min)
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        for item in response.get('items', []):
            video_info = {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt']
            }
            videos.append(video_info)

        return videos

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

# Example: Get video details
def get_video_details(youtube, video_id):
    """
    Get detailed information about a specific video

    Args:
        youtube: YouTube API client
        video_id: YouTube video ID

    Returns:
        Dictionary with video details
    """
    try:
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            item = response['items'][0]
            return {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0),
                'comment_count': item['statistics'].get('commentCount', 0),
                'duration': item['contentDetails']['duration']
            }
        return None

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

# Example: Get video comments
def get_video_comments(youtube, video_id, max_results=20):
    """
    Get comments for a specific video

    Args:
        youtube: YouTube API client
        video_id: YouTube video ID
        max_results: Maximum number of comments to return (default: 20)

    Returns:
        List of comment dictionaries
    """
    try:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText',
            order='relevance'  # Can also be 'time' for chronological
        )
        response = request.execute()

        comments = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comment_info = {
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'like_count': comment['likeCount'],
                'published_at': comment['publishedAt'],
                'reply_count': item['snippet']['totalReplyCount']
            }
            comments.append(comment_info)

        return comments

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        if 'commentsDisabled' in str(e):
            print("Comments are disabled for this video.")
        return []

# Example: Get comprehensive video information
def get_comprehensive_video_info(youtube, video_id):
    """
    Get comprehensive information about a video including all available details

    Args:
        youtube: YouTube API client
        video_id: YouTube video ID

    Returns:
        Dictionary with comprehensive video information
    """
    try:
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails,topicDetails,status',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']

            info = {
                # Basic info
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],

                # Tags and categories
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId'),

                # Statistics
                'view_count': statistics.get('viewCount', 0),
                'like_count': statistics.get('likeCount', 0),
                'comment_count': statistics.get('commentCount', 0),

                # Content details
                'duration': content_details['duration'],
                'dimension': content_details.get('dimension'),  # 2d or 3d
                'definition': content_details.get('definition'),  # hd or sd
                'caption': content_details.get('caption'),  # true/false if captions available

                # Topic details (if available)
                'topic_categories': item.get('topicDetails', {}).get('topicCategories', []),

                # Status
                'privacy_status': item.get('status', {}).get('privacyStatus'),
                'license': item.get('status', {}).get('license'),
            }

            return info
        return None

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

# Example: Get channel information
def get_channel_info(youtube, channel_id):
    """
    Get information about a YouTube channel

    Args:
        youtube: YouTube API client
        channel_id: YouTube channel ID

    Returns:
        Dictionary with channel information
    """
    try:
        request = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            id=channel_id
        )
        response = request.execute()

        if response['items']:
            item = response['items'][0]
            return {
                'channel_id': channel_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'custom_url': item['snippet'].get('customUrl'),
                'published_at': item['snippet']['publishedAt'],
                'subscriber_count': item['statistics'].get('subscriberCount', 0),
                'video_count': item['statistics'].get('videoCount', 0),
                'view_count': item['statistics'].get('viewCount', 0),
            }
        return None

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None

# Example usage
if __name__ == '__main__':
    # Initialize YouTube client
    youtube = get_youtube_client()

    # Example 1: Search for videos
    print("=" * 80)
    print("EXAMPLE 1: Searching for Disco soul dance shimmy tutorial videos")
    print("=" * 80)
    search_query = 'Disco soul dance shimmy tutorial'
    print(f"Searching for '{search_query}' videos...\n")
    videos = search_videos(youtube, search_query, max_results=2)

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']}")
        print(f"   Channel: {video['channel']}")
        print(f"   Video ID: {video['video_id']}")
        print(f"   URL: https://www.youtube.com/watch?v={video['video_id']}")
        print(f"   Description (first 100 chars): {video['description'][:100]}...")
        print()

    if videos:
        test_video_id = videos[0]['video_id']

        # Example 2: Get comprehensive video information
        print("\n" + "=" * 80)
        print("EXAMPLE 2: Comprehensive video information")
        print("=" * 80)
        print(f"Getting comprehensive info for video: {test_video_id}\n")

        comprehensive_info = get_comprehensive_video_info(youtube, test_video_id)
        if comprehensive_info:
            print(f"Title: {comprehensive_info['title']}")
            print(f"Channel: {comprehensive_info['channel_title']}")
            print(f"Published: {comprehensive_info['published_at']}")
            print(f"Duration: {comprehensive_info['duration']}")
            print(f"Views: {int(comprehensive_info['view_count']):,}")
            print(f"Likes: {int(comprehensive_info['like_count']):,}")
            print(f"Comments: {int(comprehensive_info['comment_count']):,}")
            print(f"Definition: {comprehensive_info['definition']}")
            print(f"Has Captions: {comprehensive_info['caption']}")
            print(f"Privacy: {comprehensive_info['privacy_status']}")
            print(f"Tags: {', '.join(comprehensive_info['tags'][:5]) if comprehensive_info['tags'] else 'None'}")
            print(f"\nDescription:\n{comprehensive_info['description'][:300]}...")

        # Example 3: Get video comments
        print("\n" + "=" * 80)
        print("EXAMPLE 3: Video comments")
        print("=" * 80)
        print(f"Getting comments for video: {test_video_id}\n")

        comments = get_video_comments(youtube, test_video_id, max_results=3)
        if comments:
            print(f"Found {len(comments)} comments:\n")
            for i, comment in enumerate(comments, 1):
                print(f"{i}. {comment['author']} ({comment['like_count']} likes, {comment['reply_count']} replies)")
                comment_text = comment['text'][:150].replace('\n', ' ')
                print(f"   {comment_text}{'...' if len(comment['text']) > 150 else ''}")
                print()
        else:
            print("No comments found or comments are disabled.")

        # Example 4: Get channel information
        if comprehensive_info:
            print("\n" + "=" * 80)
            print("EXAMPLE 4: Channel information")
            print("=" * 80)
            channel_id = comprehensive_info['channel_id']
            print(f"Getting channel info for: {channel_id}\n")

            channel_info = get_channel_info(youtube, channel_id)
            if channel_info:
                print(f"Channel: {channel_info['title']}")
                print(f"Custom URL: {channel_info.get('custom_url', 'N/A')}")
                print(f"Subscribers: {int(channel_info['subscriber_count']):,}")
                print(f"Total Videos: {int(channel_info['video_count']):,}")
                print(f"Total Views: {int(channel_info['view_count']):,}")
                print(f"Created: {channel_info['published_at']}")
                print(f"\nChannel Description:\n{channel_info['description'][:300]}...")

