import os
import json
import re
import datetime
from pathlib import Path
import time
from unicodedata import name
import pandas as pd
import tweepy

consumer_key = "86xM43yUqYsDOVEEG9l4QSlTE"
consumer_secret = "W1jB00fdVVzRzyQd8p9mJnzKC9XAGQRqCP5G4hRKnoA3KM1Dna"
access_key = "1156738416-CiGsQPHyWVUieqnCyDfWBz3OLqfpKDpiljj9zcr"
access_secret = "P8UDrYvC9LnOIblV5WWgBvoTXkjNqHxzN2PUTyHivC0EW"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

def scrape_hashtag(tweet_object, path, root):
        '''
        Extract the relavant tweets based on hashtag
        '''
        date_since = datetime.datetime.fromtimestamp(tweet_object['created_at']).date()
        # find all hashtags in tweet_object['text']
        # (except the case when hashtag is the beginning of the text)
        list_hashtag = re.findall(r"\s+#(\w+)", tweet_object['text'])
        num_tweet = 20
        
        # handle the corner case of tweet_object['text'] beginning with '#'
        if len(tweet_object['text']) != 0 and tweet_object['text'][0] == '#':
                list2 = re.findall("#(\w+)", tweet_object['text'])
                if len(list2) != 0:
                        first_hashtag = list2[0]
                        list_hashtag.append(first_hashtag)

        # corner case
        if len(list_hashtag) == 0:
                return

        for hashtag_text in list_hashtag:
                db = pd.DataFrame(columns=['username',
                                        'description',
                                        'location',
                                        'following',
                                        'followers',
                                        'total_tweets',
                                        'retweet_count',
                                        'text',
                                        'hashtags'])

                # Use .Cursor() to search through twitter for the required tweets.
                hashtag_tweets = []
                try:
                        hashtag_tweets = api.search_tweets(hashtag_text, lang="en", since_id=date_since, count=num_tweet)
                except Exception as e:
                	if str(e)[:3] != "401" and str(e)[:3] != "404":
                                print(str(e))
                                time.sleep(3.0)
                                scrape_hashtag(tweet_object, path, root)

                # .Cursor() returns an iterable object
                # Each item in iterator has various attributes to get information about each tweet
                list_tweets = [tweet for tweet in hashtag_tweets]
                if list_tweets == []: # corner case
                        return

                # tweet count counter
                i = 1

                for tweet in list_tweets:
                        # extract all details of 'tweet'
                        username = tweet.user.screen_name
                        description = tweet.user.description
                        location = tweet.user.location
                        following = tweet.user.friends_count
                        followers = tweet.user.followers_count
                        total_tweets = tweet.user.statuses_count
                        retweet_count = tweet.retweet_count
                        hashtags = tweet.entities['hashtags']

                        # Retweets can be distinguished by a retweeted_status attribute,
                        # in case it is an invalid reference, except block will be executed
                        try:
                                text = tweet.retweeted.text
                        except AttributeError:
                                text = tweet.text

                        hashtext = list()
                        for j in range(0, len(hashtags)):
                                hashtext.append(hashtags[j]['text'])
        
                        # append all the extracted information in a DataFrame
                        ith_tweet = [username, description,
                                location, following,
                                followers, total_tweets,
                                retweet_count, text, hashtext]

                        db.loc[len(db)] = ith_tweet
                        i = i+1

                # store the related tweet in a csv file
                path_parts = list(Path(path).parts) # list of various parts of 'path' of the current tweets.json file
                path_parts.pop() # remove the last element (i.e, tweets.json)
                path_parts[0] = root # change the root
                path_parts[1] = "tweet_" + str(tweet_object['tweet_id']) # name of the folder to store in
                new_folder_name = str(Path(*path_parts))
                filename = "hashtag_" + str(hashtag_text) + ".csv"

                os.makedirs(new_folder_name, exist_ok=True) # Create the directory

                # save database as a CSV file
                with open(os.path.join(new_folder_name, filename), 'w') as f:
                        db.to_csv(f)

def scrape_mention(tweet_object, path, root):
        '''
        Extract the relavant tweets based on mention
        '''
        date_since = datetime.datetime.fromtimestamp(tweet_object['created_at']).date()
        # find all mentions in tweet_object['text']
        # (except the case when hashtag is the beginning of the text)
        list_mention = re.findall(r"\s+@(\w+)", tweet_object['text'])
        num_tweet = 20

        # handle the corner case of tweet_object['text'] beginning with '@'
        if len(tweet_object['text']) != 0 and tweet_object['text'][0] == '@':
                list2 = re.findall("@(\w+)", tweet_object['text'])
                if len(list2) != 0:
                        first_mention = list2[0]
                        list_mention.append(first_mention)
        
        # corner case
        if len(list_mention) == 0:
                return

        for mention_text in list_mention:                
                db = pd.DataFrame(columns=['username',
                                        'description',
                                        'location',
                                        'following',
                                        'followers',
                                        'total_tweets',
                                        'retweet_count',
                                        'text',
                                        'hashtags'])

                # Use .Cursor() to search through twitter for the required tweets.
                mention_tweets = []
                try:
                        mention_tweets = api.user_timeline(screen_name=mention_text, count=num_tweet, since_id=date_since)
                except Exception as e:
                	if str(e)[:3] != "401" and str(e)[:3] != "404":
                                print(str(e))
                                time.sleep(3.0)
                                scrape_mention(tweet_object, path, root)

                # .Cursor() returns an iterable object
                # Each item in iterator has various attributes to get information about each tweet
                list_tweets = [tweet for tweet in mention_tweets]
                if list_tweets == []: # corner case
                        return

                # tweet count counter
                i = 1

                for tweet in list_tweets:
                        username = tweet.user.screen_name
                        description = tweet.user.description
                        location = tweet.user.location
                        following = tweet.user.friends_count
                        followers = tweet.user.followers_count
                        total_tweets = tweet.user.statuses_count
                        retweet_count = tweet.retweet_count
                        hashtags = tweet.entities['hashtags']
        
                        # Retweets can be distinguished by
                        # a retweeted_status attribute,
                        # in case it is an invalid reference,
                        # except block will be executed
                        try:
                                text = tweet.retweeted.text
                        except AttributeError:
                                text = tweet.text

                        hashtext = list()
                        for j in range(0, len(hashtags)):
                                hashtext.append(hashtags[j]['text'])
        
                        # Here we are appending all the
                        # extracted information in the DataFrame
                        ith_tweet = [username, description,
                                location, following,
                                followers, total_tweets,
                                retweet_count, text, hashtext]

                        db.loc[len(db)] = ith_tweet

                        # Function call to print tweet data on screen
                        # print_tweet_data(i, ith_tweet)
                        i = i+1


                ## store the related tweet in a csv file
                path_parts = list(Path(path).parts) # list of various parts of 'path' of the current tweets.json file
                path_parts.pop() # remove the last element (i.e, tweets.json)
                path_parts[0] = root # change the root
                path_parts[1] = "tweet_" + str(tweet_object['tweet_id']) # name of the folder to store in
                new_folder_name = str(Path(*path_parts))
                filename = "mention_" + str(mention_text) + ".csv"

                os.makedirs(new_folder_name, exist_ok=True) # Create the directory

                # save database as a CSV file.
                with open(os.path.join(new_folder_name, filename), 'w') as f:
                        db.to_csv(f)
                print(os.path.join(new_folder_name, filename))


def start_scraping(filename):
    '''
    Iterate over all the files of 'filename' folder and process
    all files named 'tweets.json'.

    Parameters:
    filename: The name of the root directory which contains all
    the tweets

    Returns:
    None
    '''
    rootdir = filename
    rootdir_related_tweets = filename + "_related_tweets"
    for subdir, _, files in os.walk(rootdir): # iterate over all sub-directories and files of rootdir
        for file_name in files:
            if file_name == 'tweets.json':
                file = open(os.path.join(subdir, file_name))
                print(os.path.join(subdir, file_name))
                data = json.load(file)
                tweets = data['tweets']
                for tweet in tweets: # process every tweet of the current file
                    scrape_hashtag(tweet, os.path.join(subdir, file_name), rootdir_related_tweets)
                    scrape_mention(tweet, os.path.join(subdir, file_name), rootdir_related_tweets)

                # Closing file
                file.close()

if __name__ == '__main__':
        start_scraping('politifact_fake') # scrape fake tweets
        start_scraping('politifact_real') # scrape real tweets
