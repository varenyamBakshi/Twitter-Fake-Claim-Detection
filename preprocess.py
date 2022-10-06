from sentence_transformers import SentenceTransformer
import pandas as pd
from entailment import entailment_model
from create_dataset import process_all_tweets

print("Loading mpnet model....")
mpnet = SentenceTransformer('stsb-mpnet-base-v2')
print("mpnet model loaded!")    

print("Creation of dataset politifact_dataset_hashtags_and_mentions.csv started ...")
train_df_real = process_all_tweets(rootdir='./politifact_real', model=mpnet)
train_df_fake = process_all_tweets(rootdir='./politifact_fake', model=mpnet)
frames = [train_df_real, train_df_fake]
train_df = pd.concat(frames)
train_df = train_df.sample(frac=1).reset_index() # shuffle related tweets data and reset index

# save data in a single csv file
train_df.to_csv("politifact_dataset_hashtags_and_mentions.csv")
print("politifact_dataset_hashtags_and_mentions.csv created successfully!")