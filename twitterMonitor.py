from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd
from discord_webhook import DiscordWebhook, DiscordEmbed
import time

import twitterCred

# CREATES TWITTER CLIENT FOR CONTROL


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()  # Authorization
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets


# AUTHENTICATES TWITTER CONNECTION FOR CLIENT. KEYS FOUND IN twitter_cred.py
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitterCred.CONSUMER_KEY, twitterCred.CONSUMER_KEY_SECRET)
        auth.set_access_token(twitterCred.ACCESS_TOKEN, twitterCred.ACCESS_TOKEN_SECRET)
        return auth


# STREAMS DATA
class TwitterStreamer():
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, id_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener, filter_level=['low'])

        stream.filter(follow=id_list)


# LISTENS FOR EVENTS
class TwitterListener(StreamListener):
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):  # REACTS TO INCOMING DATA FROM TWITTER
        try:
            main_function(1)
            # print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print('Error on_data: %s' % str(e))
        return True

    def on_error(self, status):  # ERROR CHECK
        print(status)
        if status == 420:  # RATE LIMIT ERROR AVOIDANCE
            time.sleep(15 * 60)  # 15 MINUTE WAIT TO RESET LIMIT OR UNCOMMENT FALSE TO EXIT
            pass
            # return False


# RETURNS TWEETS DATA TO PANDAS DF
class TweetInfo():
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        return df


# REPEATS NAME==MAIN ON SMALLER SCALE IF NEEDED (reduce rate limit chances)
def main_function(count_num):
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweet_info = TweetInfo()

    discord_wh_url = twitterCred.DISCORD_WH_URL
    hook = DiscordWebhook(url=discord_wh_url, username='ScrapeyBoi')
    embed = DiscordEmbed(title='NEW TWEET', description='https://twitter.com/RestockWorld/with_replies?lang=en', color=242424)
    tweets = api.user_timeline(id='1075875489603076096', count=count_num)
    df = tweet_info.tweets_to_data_frame(tweets)

    print(df.head(count_num))

    if hasattr(tweets[0], 'retweeted_status'):
        pass
        # print('\nRETWEET')
    else:
        if 'media' in tweets[0].extended_entities:
            for image in tweets[0].extended_entities['media']:
                embed.set_image(url=image['media_url'])
        else:
            embed.set_image(url='http://proxy6006.appspot.com/u?purl=MDA1eDAwNTEvMDIxMDAxMzY1MS82OTA2NzAzMDY5ODQ1Nzg1NzAxL3NyZW5uYWJfZWxpZm9ycC9t%0Ab2MuZ21pd3Quc2JwLy86c3B0dGg%3D%0A')

        embed.set_thumbnail(url='https://twitter.com/RestockWorld/with_replies?lang=en')
        embed.add_embed_field(name='Tweet: ', value=tweets[0].text)
        embed.set_timestamp()
        hook.add_embed(embed)
        hook.execute()

    id_list = ['1075875489603076096']
    #'3309125130'

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets('tweets.json', id_list)


if __name__ == "__main__":
    main_function(3)
