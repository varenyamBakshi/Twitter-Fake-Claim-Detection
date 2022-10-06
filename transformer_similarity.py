from sentence_transformers import util
import numpy as np

def retrieve_topk(model, premise_corpus, hypothesis, k):
    '''
    Retreive top 'k' premises from the 'premise_corpus' ranked according to decreasing
    similarity with 'hypothesis' as predicted by the 'model'

    Parameters:
    model: The model used for computing similarity
    premise_corpus: A list of strings consisting of premises to be compared against 'hypothesis'
    hypothesis: String with which the premise_corpus is to be compared
    '''
    # base case
    if len(premise_corpus) == 0: 
        return []

    k = min(k, len(premise_corpus))

    # encode premise_corpus to get corpus embeddings
    premise_corpus_embeddings = model.encode(premise_corpus, convert_to_tensor = True)
    # print(premise_corpus_embeddings.shape)

    # encode hypothesis to get sentence embeddings
    hypothesis_embedding = model.encode(hypothesis, convert_to_tensor = True)
    # print(hypothesis_embedding.shape)

    # compute similarity scores of the sentence with the corpus
    cos_scores = util.pytorch_cos_sim(hypothesis_embedding, premise_corpus_embeddings)[0]

    # sort the results in decreasing order and get the first top_k
    top_k_premises = np.argpartition(-cos_scores, range(k))[0:k]

    ## FOR DEBUGGING
    # print(f'Hypothesis:, {hypothesis},\n')
    # print(f'Top, {k}, most similar sentences in corpus:')

    # for idx in top_k_premises[0:k]:
    #     print(f'{premise_corpus[idx]}, (Score: {cos_scores[idx]:.4f})')
    ##

    # return the premises which have k highest semantic similarity with the hypothesis
    premise_strings = []
    for idx in top_k_premises[0:k]:
        premise_strings.append(premise_corpus[idx])

    return premise_strings