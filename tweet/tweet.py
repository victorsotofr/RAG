import os
import tweepy as tw
import pandas as pd
from tqdm import tqdm
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def twitter_connection():
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer_token:
        logger.error("Twitter Bearer Token is not set in environment variables.")
        raise ValueError("Twitter Bearer Token is not set in environment variables.")

    client = tw.Client(bearer_token=bearer_token)
    return client

def create_cursor(client, user_handle, count=100):
    try:
        # Collect tweets from the user's timeline using API v2
        user = client.get_user(username=user_handle)
        user_id = user.data.id
        tweets = client.get_users_tweets(id=user_id, max_results=count)

        logger.info("Retrieving new tweets...")
        tweets_copy = []
        for tweet in tqdm(tweets.data):
            tweets_copy.append(tweet)

        logger.info(f"New tweets retrieved: {len(tweets_copy)}")
        return tweets_copy
    except Exception as e:
        logger.error(f"Error retrieving tweets: {e}")
        raise

def build_dataset(tweets_copy):
    tweets_list = []
    for tweet in tqdm(tweets_copy):
        hashtags = []
        try:
            for hashtag in tweet.entities["hashtags"]:
                hashtags.append(hashtag["text"])
        except:
            pass
        tweets_list.append({
            'id': tweet.id,
            'user_name': tweet.user.name,
            'user_location': tweet.user.location,
            'user_description': tweet.user.description,
            'user_created': tweet.user.created_at,
            'user_followers': tweet.user.followers_count,
            'user_friends': tweet.user.friends_count,
            'user_favourites': tweet.user.favourites_count,
            'user_verified': tweet.user.verified,
            'date': tweet.created_at,
            'text': tweet.text,  # Use text to get the complete tweet text
            'hashtags': hashtags if hashtags else None,
            'source': tweet.source,
            'retweets': tweet.retweet_count,
            'favorites': tweet.favorite_count,
            'is_retweet': tweet.retweeted
        })
    tweets_df = pd.DataFrame(tweets_list)
    return tweets_df

def update_and_save_dataset(tweets_df):
    file_path = "paris_2024_tweets.csv"
    if os.path.exists(file_path):
        tweets_old_df = pd.read_csv(file_path)
        logger.info(f"Past tweets: {tweets_old_df.shape}")
        tweets_all_df = pd.concat([tweets_old_df, tweets_df], axis=0)
        logger.info(f"New tweets: {tweets_df.shape[0]} Past tweets: {tweets_old_df.shape[0]} All tweets: {tweets_all_df.shape[0]}")
        tweets_new_df = tweets_all_df.drop_duplicates(subset=["id"], keep='last')
        logger.info(f"All tweets: {tweets_new_df.shape}")
        tweets_new_df.to_csv(file_path, index=False)
    else:
        logger.info(f"Tweets: {tweets_df.shape}")
        tweets_df.to_csv(file_path, index=False)

if __name__ == "__main__":
    try:
        client = twitter_connection()
        tweets_copy = create_cursor(client=client, user_handle="Paris2024", count=100)
        tweets_df = build_dataset(tweets_copy)
        update_and_save_dataset(tweets_df)
    except Exception as e:
        logger.error(f"An error occurred: {e}")