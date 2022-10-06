import json
import os
import pandas as pd
from transformer_similarity import retrieve_topk

def walk_over(func):
    '''
    Decorator to iterate over kwargs['rootdir'] directory

    Iterates over all files in the kwargs['rootdir'] and
    calls func for each of the files with 'file_path' and
    'file_name' added to kwargs

    Parameters:
    func: Function to be called for each file

    Returns
    inner: Modified function to be called for processing all the files
    '''
    global train_df, num_tweets_processed

    # track the number of tweets processed
    num_tweets_processed = 0

    # store the training data as a pandas DataFrame
    train_df = pd.DataFrame(columns=["Tweet", "TweetCreatedAt", "TopKHashAndMentionTweets", "Label"])
 
    def inner(**kwargs):
        rootdir = kwargs['rootdir']
        for subdir, _, files in os.walk(rootdir):
            for file_name in files:
                kwargs['file_path'] = os.path.join(subdir, file_name)
                kwargs['file_name'] = file_name
                func(**kwargs)
        
        return train_df

    return inner

@walk_over
def process_all_related_tweets(**kwargs):
    '''
    Process all the related tweets for a given tweet given kwargs['rootdir']
    of the related tweets

    Iterate over all the tweets related to a given tweet and append the
    hash tag relted tweets to related_tweets['hash'] and mention tweets to
    related_tweets['mention']

    Parameters:
    kwargs.file_path: The path of the csv file containing hash/mention tweets
    kwargs.file_name: The name of the csv file
    kwargs.related_tweets: Dictionary to store the related tweets

    Returns:
    None
    '''
    file_path = kwargs['file_path'] # path of current file being processed
    file_name = kwargs['file_name'] # name of current file being processed
    related_tweets = kwargs['related_tweets'] # dictionary to store the related tweets of current tweet
    try:
        file_type = file_name.split('_')[0]
        df = pd.read_csv(file_path)
        if file_type == 'hashtag': # df contains related tweets with one of the same hashtags in original tweet
            related_tweets['hash'].append(df['text'].to_list())
        elif file_type == 'mention': # df contains related tweets with one of the mentions referred in original tweet
            related_tweets['mention'].append(df['text'].to_list())
        else: # file_type cannot be anything other than 'hash' or 'mention'
            raise Exception(f'Invalid file_type: {file_type}!')
    except Exception as e:
        print(f'Invalid file name: {file_name}')
        print(e)

@walk_over
def process_all_tweets(**kwargs):
    '''
    Function responsible for training the over the entire dataset

    Iterates over all the tweets in both 'politifact_fake' and 'politifact_real'
    dataset and processes all the related tweets for each of the tweet in both
    the directories to classify the tweet as 'fake' or 'real'

    Parameters:
    kwargs.rootdir: The root directory path that is to be processed

    Returns:
    None
    '''
    global train_df, num_tweets_processed
    label = '' # ground truth label of current tweet content

    if kwargs['rootdir'] == './politifact_fake':
        label = 'fake'
    else: 
        label = 'real'

    file_path = kwargs['file_path']
    file_name = kwargs['file_name']
    model = kwargs['model'] # pre-trained model to use for classification
    file = open(file_path)

    if file_name == 'tweets.json': # only process the file containing tweets
        data = json.load(file)
        tweets = data['tweets']

        for tweet in tweets:
            try:
                tweet_id = tweet['tweet_id']
                related_rootdir = os.path.join(kwargs['rootdir'] + '_related_tweets', f'tweet_{tweet_id}')

                # create the related_tweets dictionary to store all the related tweets
                related_tweets = {'tweet': tweet['text'], 'hash': [], 'mention': []}
                process_all_related_tweets(rootdir=related_rootdir, related_tweets=related_tweets)

                # store all the related tweets as python lists
                all_hash = [item for sublist in related_tweets['hash'] for item in sublist]
                all_mention = [item for sublist in related_tweets['mention'] for item in sublist]

                # retreive top 5 related tweets as per the model
                top_k_premises = retrieve_topk(model, all_hash + all_mention, str(tweet['text']), 5)
                top_k_premises_concatenate = " ".join(top_k_premises)

                # construct the training dataset as a pandas DataFrame
                train_df.loc[train_df.shape[0]] = [str(tweet['text']), tweet['created_at'], top_k_premises_concatenate, label]

                num_tweets_processed += 1
                
                # print status every 5000 tweets processed
                if (num_tweets_processed % 5000 == 0):
                    print(str(num_tweets_processed) + " tweets processed.")
                    print("train_df shape:", train_df.shape)
                    print()

            except Exception as e:
                # print(e)
                pass
