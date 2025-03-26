"""Test script to verify Twitter Manager functionality."""
from src.twitter_manager import TwitterManager

def main():
    try:
        # Initialize the Twitter Manager
        manager = TwitterManager()
        
        # Generate and post one tweet
        success = manager.generate_and_post()
        
        if success:
            print("Tweet posted successfully!")
            
            # Get stats
            stats = manager.get_stats()
            print("\nCurrent stats:")
            print(f"Total posts: {stats['total_posts']}")
            print(f"Successful posts: {stats['successful_posts']}")
            print(f"Failed posts: {stats['failed_posts']}")
        else:
            print("Failed to post tweet. Check logs for details.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()