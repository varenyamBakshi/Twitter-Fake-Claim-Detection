# This file processes the dataset of hashtag and mention tweets 
# and creates training dataset

import pandas as pd
from transformer_similarity import retrieve_topk
from ner import return_named_entities
from entailment import entailment_without_finetuning
from wiki_and_news_retrieval import retrieve_news, retrieve_wiki
import datetime
import nltk
nltk.download('punkt')

def process_dataset(model):
    # True Positive, True Negative, False Positive and False Negative
    TP, TN, FP, FN = 0, 0, 0, 0
    accuracy = 0

    # construct the train data set
    train_df = pd.DataFrame(columns=["Tweet(Hypothesis)", "RelevantSentences(Premise)", "Label"])
    tweet_df = pd.read_csv("politifact_dataset_hashtags_and_mentions.csv")

    batch=20
    num = 0

    for idx in range(len(tweet_df)):
        try:
            if batch == 0:
                train_df.dropna(inplace=True)
                train_df = train_df.sample(frac=1).reset_index()
                train_df.to_csv(f"training_dataset_{num}.csv")
                print(f"training_dataset_{num}.csv generated successfully!............")
                train_df = pd.DataFrame(columns=["Tweet(Hypothesis)", "RelevantSentences(Premise)", "Label"])
                num += 1
                batch=20

            tweet = tweet_df.loc[idx, "Tweet"] # current tweet
            tweetCreatedAt = tweet_df.loc[idx, "TweetCreatedAt"]
            top_k_premises = tweet_df.loc[idx, "TopKHashAndMentionTweets"] # top k premises
            label = tweet_df.loc[idx, "Label"]

            combined_hypo_and_prem = tweet + " " + top_k_premises

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
                date_since = datetime.datetime.fromtimestamp(tweetCreatedAt).date()
                entity_news = retrieve_news(entity, num_documents=2, associated_tweet_date=date_since)
                news_articles.extend(entity_news)

            # retrieve top 5 documents out of the combined list
            print("Retrieving top 5 out of wikipedia and news articles ... ")
            retrieved_docs = retrieve_topk(model, wikipedia_docs + news_articles, tweet, 5)


            ## do the sentence selection
            # first find the sentence list for each retrieved doc
            all_sentences = []
            for doc in retrieved_docs:
                doc_sentences = nltk.tokenize.sent_tokenize(doc)
                all_sentences.extend(doc_sentences)

            # retrieve top 5 sentences out of all the sentences in the top 5 retrieved documents
            print("Retrieving top 5 sentences from the retrieved documents - sentence selection ... ")
            relevant_sentences = retrieve_topk(model, all_sentences, tweet, 5)

            # add the tweet, relevant sentences to the csv file
            relevant_sentences_premise = " ".join(relevant_sentences)
            train_df.loc[train_df.shape[0]] = [tweet, relevant_sentences_premise, label]
            batch -= 1

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
            print("Label: " + label + " , prediction = " + prediction)
            print("accuracy =", accuracy)
            print("train_df shape:", train_df.shape)
            print()
        except:
            pass

    # after all the tweets have been processed
    train_df.dropna(inplace=True)
    train_df = train_df.sample(frac=1).reset_index()
    train_df.to_csv(f"training_dataset_{num}.csv")
    print(f"training_dataset_{num}.csv generated successfully!............")
    print("#### Accuracy on the whole dataset without finetuning is: ", accuracy)

