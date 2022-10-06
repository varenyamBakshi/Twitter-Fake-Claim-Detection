import json
import os
import pandas as pd
import datetime
from entailment import entailment_without_finetuning
import nltk
import random
nltk.download('punkt')

from transformer_similarity import retrieve_topk
from ner import return_named_entities
from wiki_and_news_retrieval import retrieve_news, retrieve_wiki

num_tweets_processed = 0
tweet_list = []
relevant_sentences_list = []
labels_list = []

def walk_over(func):
    def inner(**kwargs):
        rootdir = kwargs['rootdir']
        for subdir, _, files in os.walk(rootdir):
            for file_name in files:
                kwargs['file_path'] = os.path.join(subdir, file_name)
                kwargs['file_name'] = file_name
                func(**kwargs)

    return inner

def walk_over_for_dataframe(func):
    global train_df, num_tweets_processed, TP, TN, FP, FN
    num_tweets_processed = 0
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    train_df = pd.DataFrame(columns=['hypothesis', 'premise', 'label'])
    def inner(**kwargs):
        for (subdir1, _, files1), (subdir2, _, files2) in zip(os.walk('./politifact_fake'), os.walk('./politifact_real')):
            print(subdir1)
            print(subdir2)
            for (file_name1, file_name2) in zip(files1, files2):
                kwargs['file_path'] = os.path.join(subdir1, file_name1)
                kwargs['file_name'] = file_name1
                kwargs['rootdir'] = './politifact_fake'
                func(**kwargs)
            # for file_name in files2:
                kwargs['file_path'] = os.path.join(subdir2, file_name2)
                kwargs['file_name'] = file_name2
                kwargs['rootdir'] = './politifact_real'
                func(**kwargs)

        # return train_df

    return inner

@walk_over
def process_all_related_tweets(**kwargs):
    file_path = kwargs['file_path']
    file_name = kwargs['file_name']
    related_tweets = kwargs['related_tweets']
    try:
        file_type = file_name.split('_')[0]
        df = pd.read_csv(file_path)
        if file_type == 'hashtag':
            related_tweets['hash'].append(df['text'].to_list())
        elif file_type == 'mention':
            related_tweets['mention'].append(df['text'].to_list())
        else:
            raise Exception(f'Invalid file_type: {file_type}!')
        print(f'\t{file_name}')
    except Exception as e:
        print(f'Invalid file name: {file_name}')
        print(e)

@walk_over_for_dataframe
def process_all_tweets(**kwargs):
    global train_df, num_tweets_processed
    global TP, TN, FP, FN
    label = ""
   
    if kwargs['rootdir'] == './politifact_fake':
        print("fake")
        label = "fake"
    else: 
        print("real")
        label = "real"

    file_path = kwargs['file_path']
    file_name = kwargs['file_name']
    model = kwargs['model']
    file = open(file_path)

    if file_name == 'tweets.json':
        data = json.load(file)
        tweets = data['tweets']
        for i, tweet in enumerate(tweets):
            if(i == 2):
                break
            print(f'{i} of {len(tweets)} done!')
            tweet_id = tweet['tweet_id']
            related_rootdir = os.path.join(kwargs['rootdir']+"_related_tweets", f'tweet_{tweet_id}')
            related_tweets = {'tweet': tweet['text'], 'hash': [], 'mention': []}
            process_all_related_tweets(rootdir=related_rootdir, related_tweets=related_tweets)

            # trim_related_tweets_and_call_model
            all_hash = [item for sublist in related_tweets['hash'] for item in sublist]
            all_mention = [item for sublist in related_tweets['mention'] for item in sublist]

            print("Retrieving top k tweets out of all hashtags and mention tweets ... ")
            top_k_premises = retrieve_topk(model, all_hash + all_mention, related_tweets['tweet'], 5)
            # get a <class 'torch.Tensor'>

            combined_hypo_and_prem = tweet['text']
            for premise in top_k_premises:
                combined_hypo_and_prem += " " + premise

            # pick out the named entities
            print("Extracting named entities ... ")
            named_entities = return_named_entities(combined_hypo_and_prem)

            # retrieve wikipedia documents using these named entities
            print("Retrieving wikipedia docs ... ")
            wikipedia_docs = []
            for entity in named_entities:
                entity_wikidocs = retrieve_wiki(entity, num_documents=5, num_sentences=3)
                wikipedia_docs.extend(entity_wikidocs)
            
            # retrieve news articles using these named entities
            print("Retrieving news articles ... ")
            news_articles = []
            for entity in named_entities:
                date_since = datetime.datetime.fromtimestamp(tweet['created_at']).date()
                entity_news = retrieve_news(entity, num_documents=2, associated_tweet_date=date_since)
                news_articles.extend(entity_news)

            # retrieve top 5 documents out of the combined list
            print("Retrieving top k out of wikipeida and news articles ... ")
            retrieved_docs = retrieve_topk(model, wikipedia_docs + news_articles, tweet['text'], 5)


            ##### Now do the sentence selection
            # first find the sentence list for each retrieved doc
            all_sentences = []
            for doc in retrieved_docs:
                doc_sentences = nltk.tokenize.sent_tokenize(doc)
                all_sentences.extend(doc_sentences)

            # now retrieve top k sentences out of these
            print("Retrieving top k sentences from the retrieved documents - sentence selection ... ")
            relevant_sentences = retrieve_topk(model, all_sentences, tweet['text'], 5)

            ###### now add the tweet, relevant sentences to the csv file
            relevant_sentences_premise = " ".join(relevant_sentences)
            prediction = entailment_without_finetuning(model, tweet['text'], relevant_sentences_premise, threshold=0.5)
            if prediction == "real" and label == "fake":
                FP += 1
            elif prediction == "real" and label == "real":
                TP += 1
            elif prediction == "fake" and label == "fake":
                TN += 1
            else:
                FN += 1

            accuracy = (TP + TN) / (TP + TN + FP + FN)
            # train_df.append({'hypothesis': tweet['text'], 'premise': relevant_sentences_premise, 'label': label}, ignore_index=True)
            num_tweets_processed += 1
            print("Label: " + label + " , prediction = " + prediction)
            print(str(num_tweets_processed) + " tweets processed, accuracy = " + str(accuracy))
            print()

        print(file)
    
    file.close()
