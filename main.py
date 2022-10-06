from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn.model_selection import train_test_split
from entailment import entailment_model
import time

from process_dataset import process_dataset

print('Loading mpnet model....')
mpnet = SentenceTransformer('stsb-mpnet-base-v2')
print('mpnet model loaded!')

print('Starting creation of training_dataset.csv from politifact_dataset_hashtags_and_mentions')
process_dataset(model=mpnet)
print('training_dataset.csv created for the entailment task')

time.sleep(5)
print('Starting to train (fine-tune distilbert-base-uncased)...')
train_df = pd.read_csv('training_dataset.csv')
train_df.sample(frac=1) # shuffle the dataset

print('train_df shape before train_test_split:', train_df.shape)
train_dataset, validation_dataset = train_test_split(train_df, test_size=0.1)
entailment_model(train_dataset, validation_dataset)