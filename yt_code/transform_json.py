"""
Transform existing dance_youtube_data.json to restructure comments:
- Remove 'author' field
- Add 'video_id' field
- Add 'comment_number' field
"""

import json
import os

def transform_existing_json(input_file='dance_youtube_data.json', output_file='dance_youtube_data_transformed.json'):
    """
    Transform existing JSON file to restructure comments
    """

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        return False

    print(f"Loading existing data from {input_file}...")

    # Load existing JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✓ Loaded data for {len(data)} dance styles")
    print("\nTransforming comment structure...")

    transformed_count = 0
    comment_count = 0

    # Transform the data
    for dance_style, dance_data in data.items():
        for video in dance_data.get('videos', []):
            video_id = video['basic_info']['video_id']
            comments = video.get('comments', [])

            # Restructure each comment
            new_comments = []
            for comment_num, comment in enumerate(comments, 1):
                # Create new comment structure (remove author, add video_id and comment_number)
                new_comment = {
                    'video_id': video_id,
                    'comment_number': comment_num,
                    'text': comment.get('text', ''),
                    'like_count': comment.get('like_count', 0),
                    'published_at': comment.get('published_at', ''),
                    'reply_count': comment.get('reply_count', 0)
                }
                new_comments.append(new_comment)
                comment_count += 1

            # Replace old comments with new structure
            video['comments'] = new_comments
            transformed_count += 1

    print(f"✓ Transformed {transformed_count} videos")
    print(f"✓ Restructured {comment_count} comments")

    # Save transformed data to new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Transformed data saved to {output_file}")

    # Create backup of original file
    backup_file = input_file.replace('.json', '_backup.json')
    print(f"\nCreating backup of original file: {backup_file}")

    # Load original again for backup (to preserve original structure)
    with open(input_file, 'r', encoding='utf-8') as orig:
        original_data = json.load(orig)

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, indent=2, ensure_ascii=False)

    # Update original file with transformed data
    print(f"Updating original file: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("TRANSFORMATION COMPLETE!")
    print("=" * 80)
    print(f"✓ Original file backed up to: {backup_file}")
    print(f"✓ Original file updated: {input_file}")
    print(f"✓ Copy saved to: {output_file}")

    # Show sample of transformed data
    print("\n" + "=" * 80)
    print("SAMPLE OF TRANSFORMED DATA")
    print("=" * 80)

    first_dance = list(data.keys())[0]
    sample_data = data[first_dance]

    print(f"\nDance: {first_dance}")
    if sample_data['videos'] and sample_data['videos'][0]['comments']:
        sample_comment = sample_data['videos'][0]['comments'][0]
        print(f"\nSample comment structure:")
        print(json.dumps(sample_comment, indent=2))

        print(f"\nBefore (had 'author' field):")
        print("  - author: [removed]")
        print(f"\nAfter (new fields):")
        print(f"  - video_id: {sample_comment['video_id']}")
        print(f"  - comment_number: {sample_comment['comment_number']}")
        print(f"  - text: {sample_comment['text'][:50]}...")
        print(f"  - like_count: {sample_comment['like_count']}")
        print(f"  - published_at: {sample_comment['published_at']}")
        print(f"  - reply_count: {sample_comment['reply_count']}")

    return True

if __name__ == '__main__':
    # Run the transformation
    transform_existing_json()

