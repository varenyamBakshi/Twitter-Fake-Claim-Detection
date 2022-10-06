import wikipedia
import random
from pynytimes import NYTAPI

wikipedia.set_lang("en")
API_KEY_PRADNESH="ewLno0bNMCm6cuDGcAiXn2vcVxkxNcoI"
nyt = NYTAPI(API_KEY_PRADNESH, parse_dates=True)

def retrieve_news(named_entity, num_documents, associated_tweet_date):
    '''
    Retrieve news documents using New York Times API sorted by relevance

    Each news document returned is defined as a concatanation of article
    title, article's abstract (i.e, summary) and the article's lead
    paragraph (i.e, the first paragraph which broadly covers the entire
    article's content in most of the cases)

    Parameters:
    named_entitye: search query
    num_documents: number of documents to retrieve
    associated_tweet_date: beginning date of search

    Returns:
    [String] => a list of strings, each of which representing a news
    document containg the information described previously
    '''
    # get all the news articles related to 'named_entity'
    news_articles = nyt.article_search(
        query = named_entity,
        results = num_documents,
        dates = {
            "begin": associated_tweet_date
        },
        options = {
            "sort": "relevance"
        }
    )

    # create the news document using the information obtained in articles
    news_documents = []
    for article in news_articles:
        try:
            article_content = ""
            article_metadata = nyt.article_metadata(url=article["web_url"])
            article_content += article_metadata[0]["title"]
            article_content += str(article["abstract"])
            article_content += " "
            article_content += str(article["lead_paragraph"])
            news_documents.append(article_content)
        except:
            pass
            # do nothing

    return news_documents

def retrieve_wiki(named_entity, num_documents, num_sentences):
    '''
    Retrieve wikipedia documents using Wikipedia API ordered randomly

    Each news document returned is defined as the summary returned
    by the Wikipedia API

    Parameters:
    named_entitye: search query
    num_documents: number of documents to retrieve
    associated_tweet_date: beginning date of search

    Returns:
    [String] => a list of strings, each of which representing a wikipedia
    document containg the information described previously
    '''
    query = named_entity
    article_list = wikipedia.search(query, results=num_documents)
    documents_list = []
    for article_name in article_list:
        try:
            article_summary = wikipedia.summary(article_name, sentences=num_sentences)
        except:
            continue

        documents_list.append(article_summary)
    
    return documents_list
