import json
from pathlib import Path

def review_parsed_tweets(file_path: str = 'parsed_tweets_output.json', num_tweets_to_review: int = 5):
    """
    Provides a simple CLI mechanism to review parsed tweets and update their review status.
    """
    parsed_tweets = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            parsed_tweets = json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Is it valid JSON?")
        return

    print(f"Starting review of {min(num_tweets_to_review, len(parsed_tweets))} tweets...")
    print("Options: (y)es - accept, (n)o - reject, (s)kip - pending, (q)uit")

    updated_tweets = parsed_tweets # Work on a copy if modifying in place is not desired

    for i, tweet_data in enumerate(updated_tweets):
        if i >= num_tweets_to_review:
            break

        print(f"\n--- Reviewing Tweet {i+1}/{min(num_tweets_to_review, len(parsed_tweets))} (ID: {tweet_data['tweet_id']}) ---")
        print(f"Raw Text: {tweet_data['raw_text']}")
        print("\nParsed Data V2:")
        print(json.dumps(tweet_data['parsed_data_v2'], indent=2, ensure_ascii=False))
        
        current_status = tweet_data['parsed_data_v2'].get('review_status', 'pending')
        current_needs_review = tweet_data['parsed_data_v2'].get('needs_review', True)
        print(f"\nCurrent Status: {current_status}, Needs Review: {current_needs_review}")

        while True:
            choice = input("Your feedback (y/n/s/q): ").lower()
            if choice == 'y':
                tweet_data['parsed_data_v2']['needs_review'] = False
                tweet_data['parsed_data_v2']['review_status'] = 'accepted'
                print("Marked as ACCEPTED.")
                break
            elif choice == 'n':
                tweet_data['parsed_data_v2']['needs_review'] = True
                tweet_data['parsed_data_v2']['review_status'] = 'rejected'
                print("Marked as REJECTED.")
                break
            elif choice == 's':
                tweet_data['parsed_data_v2']['needs_review'] = True
                tweet_data['parsed_data_v2']['review_status'] = 'pending'
                print("Marked as SKIPPED (pending).")
                break
            elif choice == 'q':
                print("Quitting review session.")
                # Save current progress before quitting
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_tweets, f, indent=2, ensure_ascii=False)
                print(f"Reviewed tweets saved to {file_path}")
                return
            else:
                print("Invalid choice. Please use y, n, s, or q.")

    print("\nReview session ended.")
    # Save all changes after the session concludes normally
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_tweets, f, indent=2, ensure_ascii=False)
    print(f"Reviewed tweets saved to {file_path}")

if __name__ == '__main__':
    # You can change the number of tweets to review here
    review_parsed_tweets(num_tweets_to_review=5)
