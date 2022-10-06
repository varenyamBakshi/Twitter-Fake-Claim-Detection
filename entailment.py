import pandas as pd
import torch
from torch.utils.data import Dataset
import os
os.environ["WANDB_DISABLED"] = "true"
import numpy as np
import torch
from torch.utils.data import Dataset
from sentence_transformers import util
from datasets import load_metric
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

task = "rte" # recognising textual entailment (1 among the 9 GLUE tasks)
metric = load_metric("glue", task) # This will be accuracy
  
# This function is to be fed into the HuggingFace Trainer API to compute the accuracy
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return metric.compute(predictions=predictions, references=labels)

# pytorch dataset class for recognising textual entailment
class RTE_Dataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# Thus us basically a pretrained "distilbert-base-uncased" finetuned for our dataset
def entailment_model(train_dataset, validation_dataset):
  print(train_dataset.shape, validation_dataset.shape)
  model_checkpoint = "distilbert-base-uncased"
  train_batch_size = 16 # Hyperparameter (can be tuned)
  val_batch_size = 16 # Hyperparameter (can be tuned)

  tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, use_fast=True)
  train_encodings = tokenizer(train_dataset["Tweet(Hypothesis)"].to_list(), train_dataset["RelevantSentences(Premise)"].tolist(), padding=True, truncation=True)
  validation_encodings = tokenizer(validation_dataset["Tweet(Hypothesis)"].to_list(), validation_dataset["RelevantSentences(Premise)"].tolist(), padding=True, truncation=True)

  label_dict = {"fake": 0, "real": 1}
  train_labels = train_dataset["Label"].map(label_dict).to_list()
  validation_labels = validation_dataset["Label"].map(label_dict).to_list()

  # creating the pytorch training and validation datasets from the tokenized encodings
  train_dataset_torch = RTE_Dataset(train_encodings, train_labels)
  validation_dataset_torch = RTE_Dataset(validation_encodings, validation_labels)

  # initialising the model and adding one output neural layer for classification
  num_labels = 2
  model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=num_labels)

  # training arguments to customize the training
  # consists some hyperparameters like weight decay, epochs
  training_args = TrainingArguments(
    evaluation_strategy = "epoch",
    save_strategy = "epoch",
    output_dir='./results',          # output directory
    num_train_epochs=10,              # total number of training epochs
    per_device_train_batch_size=train_batch_size,  # batch size per device during training
    per_device_eval_batch_size=val_batch_size,   # batch size for evaluation
    weight_decay=0.01,               # strength of weight decay
    metric_for_best_model="accuracy",
    load_best_model_at_end=True
  )

  # prints the deviceee - cuda or cpu
  print("Training device:", training_args.device)

  # using the Trainer API to specify training
  trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset_torch,         # training dataset
    eval_dataset=validation_dataset_torch,     # evaluation dataset
    compute_metrics=compute_metrics
  )

  # training the model
  trainer.train()

  # using the trained model to return the predictions object and extracting accuracy from it
  predictions = trainer.predict(test_dataset=validation_dataset_torch)
  print("Accuracy after finetuning:", predictions.metrics['test_accuracy'])

# This uses the 'stsb-mpnet-base-v2' pretrained model but it is not fine-tuned on our dataset
# generates embeddings and classifies entailmenr based on threshold
def entailment_without_finetuning(model, tweet, evidence_set, threshold):
    tweet_embedding = model.encode(tweet, convert_to_tensor=True)
    evidence_embedding = model.encode(evidence_set, convert_to_tensor = True)
    cosine_score = util.pytorch_cos_sim(tweet_embedding, evidence_embedding)
    similarity_score = cosine_score.item()
    if similarity_score > threshold:
        return "real"
    else:
        return "fake"

