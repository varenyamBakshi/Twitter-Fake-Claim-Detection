[Introduction](#introduction)
  * [Running the Project](#running-the-project)
      - [Dependencies](#dependencies)
      - [Dataset](#dataset)
      - [Data Mining](#data-mining)
      - [Data Pre-processing](#data-pre-processing)
      - [Training and Prediction](#training-and-prediction)
  <!--
  * [Model Overview](#model-overview)
      - [Flowchart](#flowchart)
  * [Source Code Overview](#source-code-overview)
  * [What did the project acheive](#what-did-the-project-acheive)
  * [Further Scope](#further-scope)
  * [👤 Authors](#👤-authors)
  * [🤝 Contributing](#🤝-contributing)
  * [Show your support](#show-your-support)
  * [Acknowledgments](#acknowledgments)
   -->

<!-- Screenshot Example -->
<!-- ![screenshot](./screenshots/Sprint_3.png) -->
# Introduction

> This is a submission for term project of the course [CS 529 - Topics and Tools in Social Media Data Mining](https://www.iitg.ac.in/cse/course-list.php?id=CS529) from [Indian Institute of Technology, Guwahati](https://iitg.ac.in/). It provides solution to the problem of fake news detection of tweets. For this, we use the following information present in a tweet:
> 1. Text content of the tweet
> 2. Related tweets on the basis hashtag
> 3. Related tweets on the basis of mentions
> 
[Back to top](#)

## Running the Project

- ### Dependencies
    #### <u>Command</u>:
        pip3 install requirements.txt

    #### <u>Purpose</u>:
    This would install all the dependencies of the project. Use Python3 for running the project.

<br>

- ### Dataset
    > Link to the dataset: https://drive.google.com/drive/folders/1gSx4S9i6Haul4TQRkoNQtj3sRHVwGFQ3

    #### <u>Instructions</u>:
    The dataset is to be downloaded and placed at the same level as the source code. First extract the downloaded zip files, and then name them as "politifact_fake" and "politifact_real".
    
    #### <u>Description of Dataset</u>:
    It consists of two types of tweets: fake and real (present in two different folders). Each folder (fake/real) consists of many sub-folders which contain many of files of which the files with the name (**tweets.json**) is of our interest which contains the tweets in the form of a python list with the elements being json objects with the following keys:
    1. text :- The content of the tweet.
    2. user_id :- Twitter account id.
    3. created_at :- Date of creation of tweet (in milliseconds).
    4. tweet_id :- Tweet id.
    5. user_name :- Username of the account that created the tweet.

<br>

- ### Data Mining
    #### <u>Command</u>:
        python3 tweet_mining.py

    ---
    <u>*NOTE*</u>:

    **I**. This step has already been executed, and you can skip it unless, you wish to use a different dataset than one given in the previous section.

    **II**. Before executing the command, ensure that the dataset root folder is present at the source file level.

    **III**. Since the dataset is huge, it has been submitted directly and is not available in a cloud storage as of now.

    ---

    #### <u>Output</u>:
    Two folders named **politifact_fake_related_tweets** and **politifact_real_related_tweets** are created which contain subfolders corresponding to each tweet that store the related tweets as described below.

    #### <u>Purpose</u>:
    The purpose of this step is to extract and store all the **realted tweets** (using hashtags and mentions) of a particular tweet. For this, we iterate over all the files of the [dataset](#dataset) and also over all the tweets within each file (**tweets.json**) and use the [Tweepy API](https://github.com/tweepy/tweepy) to perform the following:
    1. For each mention in the tweet, extract 20 tweets since the date of creation of it created by the same Twitter handle that is mentioned and store it in a csv file named **mention_<mention_text>.csv** under the folder named **tweet_<tweet_id>**.
    2. For each hashtag in the tweet, extract 20 tweets since the date of creation of it that contain the same hashtag and store it in a csv file named **hashtag_<hashtag_text>.csv** under the folder named **tweet_<tweet_id>**.

<br>

- ### Data Pre-processing
    #### <u>Command</u>:
        python3 preprocess.py

    #### <u>Output</u>:
    This step takes around 2 days. The result is a csv file containing with around 1,090,000 tweets with the following columns in it:
    1. Tweet :- The tweet text.
    2. TweetCreatedAt :- Date of creation of tweet
    3. TopKHashAndMentionTweets :- The concatanation of content of five most relavant hashtag and mention tweets related to the tweet in first column.
    4. Label :- Can be one of **fake** or **real** depending on whether the tweet (in the first column) is fake or real.

    #### <u>Purpose</u>:
    The purpose of this step is to find the five most relavant tweets of the [dataset containing the realted tweets](#data-mining). Also, it aims to buffer the training data as a csv file which would be used in the next step for training, testing and prediction.

<br>

- ### Training and Prediction
    #### <u>Command</u>:
        python3 main.py

    #### <u>Output</u>:
    This command takes a huge amount of time (on an average of 5 minutes per tweet). It produces a file named **training_data.csv** which buffers the retreived Wikipedia and New York Times articles' five most important sentences that make up the evidence set which is used to make prediction.

    This command broadly involves the following sub-steps:
    1. Retreival of evidence set and cretaion of **training_data.csv**. This step also prints the accuracy of pre-trained model after each iteration.
    2. Training of model using **training_data.csv**.
    3. Testing of the trained model is done in parallel while training after every five epochs and the accuracy is reported.

[Back to top](#)

<!--
## Model Overview
- ### Flowchart

[Back to top](#)

## Source Code Overview

[Back to top](#)

## What did the project acheive

[Back to top](#)

## Further Scope

[Back to top](#)

## 👤 Authors

- GitHub: [@sksingh1202](https://github.com/sksingh1202)
- LinkedIn: [saket-kum-singh](https://www.linkedin.com/in/saket-kum-singh/)

## 🤝 Contributing

**Although** this was an **term** project and there are just a few contributors right now (as of May 2022), we are **open to contributions**, issues, and  requests in the **future**!

[Back to top](#)

## Show your support

Give a ⭐️ (at the top right of this web-page) if you like this project!

## Acknowledgments

- **Authors** of the well-documented **frameworks**, **libraries**, and **APIs** which were used to build the project
- **Mentors** from the **Microsoft Team** who guided and more importantly kept **motivating** me throughout the entire journey of the project
- **Coding buddies** with whom I could discuss the **bugs** and **fixtures**
- **Family**, for their **moral** support and help in **testing** this product without which the outcome was improbable
- **Special** Thanks to **Ace Hacker** and **Microsoft** for all the support and for giving such a wonderful **opportunity to learn** in the form of **Engage 2021**
- **Thanks** to **every** individual who directly (or indirectly) helped me build this wonderful project

[Back to top](#)

---
OLD README
1. run "python3 preprocess.py"   - takes around 2 days - will result in a csv file with around 1090000 tweets
2. run "python3 main.py" - this will take a lot of time since it will first fetch the wiki and news articles for every tweet and estimated time is 5mins per tweet. After fetching the news articles and wikipedia docs, these will be stored in a csv file since this will be used for training purpose.

---
-->
