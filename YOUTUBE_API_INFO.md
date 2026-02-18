# YouTube API - Available Information

## Summary
The YouTube Data API v3 provides extensive information about videos, channels, comments, and more. Here's what you can access:

## 📹 Video Information

### Basic Details
- **Video ID**: Unique identifier for the video
- **Title**: Full title of the video
- **Description**: Complete description (can be very long, includes timestamps, links, etc.)
- **Published Date**: When the video was uploaded
- **Channel Name**: Creator's channel name
- **Channel ID**: Unique identifier for the channel
- **Thumbnails**: URLs for different thumbnail sizes (default, medium, high, standard, maxres)

### Statistics
- **View Count**: Total number of views
- **Like Count**: Number of likes
- **Comment Count**: Total number of comments
- **Favorite Count**: (Usually not used anymore)

### Content Details
- **Duration**: Video length in ISO 8601 format (e.g., PT15M33S = 15 minutes 33 seconds)
- **Definition**: Video quality (hd or sd)
- **Dimension**: 2d or 3d
- **Caption**: Whether captions/subtitles are available
- **Licensed Content**: Whether the video represents licensed content
- **Projection**: Video projection type (rectangular or 360)

### Categorization & Discovery
- **Tags**: All tags associated with the video
- **Category ID**: YouTube category (1=Film & Animation, 10=Music, 28=Science & Technology, etc.)
- **Topic Categories**: Wikipedia URLs for detected topics
- **Default Language**: Language of the video's metadata
- **Default Audio Language**: Language of the video's default audio track

### Status & Privacy
- **Upload Status**: processed, uploaded, etc.
- **Privacy Status**: public, unlisted, or private
- **License**: standard (YouTube) or creative commons
- **Embeddable**: Whether the video can be embedded
- **Public Stats Viewable**: Whether stats are publicly visible

## 💬 Comments Information

### Top-Level Comments
- **Author Name**: Comment author's display name
- **Author Channel ID**: Unique ID of the commenter
- **Comment Text**: Full text of the comment
- **Like Count**: Number of likes on the comment
- **Published Date**: When the comment was posted
- **Updated Date**: When the comment was last edited
- **Reply Count**: Number of replies to this comment
- **Parent ID**: For replies, the ID of the parent comment

### Comment Threads
- You can get comment replies
- Comments can be sorted by:
  - **relevance**: Most relevant comments first (default)
  - **time**: Chronological order

**Note**: Some videos have comments disabled, which will return an error.

## 📺 Channel Information

### Basic Details
- **Channel ID**: Unique identifier
- **Channel Name**: Display name
- **Description**: Full channel description
- **Custom URL**: Vanity URL (e.g., @username)
- **Published Date**: When the channel was created
- **Country**: Channel's country
- **Thumbnails**: Channel avatar/logo

### Statistics
- **Subscriber Count**: Number of subscribers (may be hidden by creator)
- **Video Count**: Total number of public videos
- **View Count**: Total views across all videos
- **Hidden Subscriber Count**: Boolean indicating if count is hidden

### Content Details
- **Uploads Playlist ID**: ID to get all uploaded videos
- **Related Playlists**: IDs for likes, favorites, etc.

## 🎬 Additional Information You Can Query

### Playlists
- Playlist items and metadata
- Order of videos in playlists
- Playlist descriptions and titles

### Captions/Subtitles
- **List available captions**: Languages available
- **Download captions**: Actual subtitle text (requires additional authentication for some)

### Live Streams
- Live streaming details
- Concurrent viewers
- Chat messages (for live streams)

### Search Results
- Videos, channels, playlists matching a query
- Filters by upload date, duration, video type, etc.

### Video Categories
- Full list of available categories by region
- Category names and IDs

## 🚫 What's NOT Available (or Limited)

### Auto-Generated Summaries
- **NOT available**: YouTube's auto-generated chapter summaries are not accessible via the API
- These are generated client-side and not exposed through the API

### Full Transcripts via API
- Captions can be listed, but downloading requires additional OAuth authentication
- Auto-generated transcripts are available but need proper authentication

### Recommendations
- The API doesn't provide YouTube's recommendation algorithm results
- You can't get "Related Videos" or "Up Next" suggestions

### Detailed Analytics
- Creator analytics (watch time, traffic sources, etc.) require OAuth and channel ownership
- Public API only gets public statistics

### Private Information
- Email addresses
- Detailed demographic information about viewers
- Revenue/monetization data

## 💡 Practical Use Cases

1. **Content Analysis**: Analyze video descriptions, tags, and titles for trends
2. **Comment Sentiment**: Analyze comment text for sentiment analysis
3. **Channel Research**: Study channel growth, upload frequency, engagement
4. **Video Discovery**: Search and filter videos by various criteria
5. **Data Collection**: Build datasets for machine learning or research
6. **Trend Analysis**: Track view counts, likes, and comments over time

## 📊 API Quotas

**Important**: The YouTube Data API has quota limits:
- Default quota: 10,000 units per day
- Different operations cost different amounts:
  - Search: 100 units
  - Video list: 1 unit
  - Comment threads: 1 unit
  - Video upload: 1600 units

Monitor your usage to avoid hitting limits!

## 🔧 Functions in Your Code

Your `Main.py` includes these functions:

1. `search_videos()` - Search for videos by keyword
2. `get_video_details()` - Get basic video information
3. `get_video_comments()` - Get video comments
4. `get_comprehensive_video_info()` - Get ALL available video data
5. `get_channel_info()` - Get channel statistics and details

## 🎯 Next Steps

To get more specific information:
- Use `get_comprehensive_video_info()` for full video details including description
- Use `get_video_comments()` for all comments with author info
- Combine multiple functions to build a complete dataset
- Add pagination to get more than the max results per query

For auto-generated summaries, you would need to:
- Parse the video description for creator-added chapters
- Use a third-party transcript service
- Implement your own summarization using the description and comments

