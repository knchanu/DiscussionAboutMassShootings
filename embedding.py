"""
code adapted from: https://github.com/ddemszky/framing-twitter
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import json
import os
import gc
import re


def word_weights(comments, a=1e-3):
    # get word frequencies
    vectorizer = CountVectorizer(decode_error='ignore')
    counts = vectorizer.fit_transform(comments)
    total_freq = np.sum(counts, axis=0).T  # aggregate frequencies over all files
    N = np.sum(total_freq)
    weighted_freq = a / (a + total_freq / N)
    gc.collect()
    # dict with words and their weights
    return dict(zip(vectorizer.get_feature_names(), weighted_freq))

def comments2idx(comments, words2index, words2weight):
    """
    Given a list of comments, output array of word indices that can be fed into the algorithms.
    :param comments: a list of comments
    :param words: a dictionary, words['str'] is the indices of the word 'str'
    :return: x1, m1. x1[i, :] is the word indices in sentence i, m1[i,:] is the mask for sentence i (0 means no word at the location)
    """
    #print(comments[0].split())
    maxlen = min(max([len(s.split()) for s in comments]), 100)
    print('maxlen', maxlen)
    n_samples = len(comments)
    print('samples', n_samples)
    x = np.zeros((n_samples, maxlen)).astype('int32')
    w = np.zeros((n_samples, maxlen)).astype('float32')
    x_mask = np.zeros((n_samples, maxlen)).astype('float32')
    for idx, s in enumerate(comments):
        if idx % 100000 == 0:
            print(idx)
        split = s.split()
        indices = []
        weightlist = []
        for word in split:
            if word in words2index:
                indices.append(words2index[word])
                if word not in words2weight:
                    weightlist.append(0.000001)
                else:
                    weightlist.append(words2weight[word])
        length = min(len(indices), maxlen)
        x[idx, :length] = indices[:length]
        w[idx, :length] = weightlist[:length]
        x_mask[idx, :length] = [1.] * length
    del comments
    gc.collect()
    return x, x_mask, w

def get_weighted_average(We, x, m, w, dim):
    """
    Compute the weighted average vectors
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in sentence i
    :param w: w[i, :] are the weights for the words in sentence i
    :return: emb[i, :] are the weighted average vector for sentence i
    """
    print('Getting weighted average...')
    n_samples = x.shape[0]
    print(n_samples, dim)
    emb = np.zeros((n_samples, dim)).astype('float32')

    for i in range(n_samples):
        if i % 100000 == 0:
            print(i)
        stacked = []
        for idx, j in enumerate(x[i, :]):
            if m[i, idx] != 1:
                stacked.append(np.zeros(dim))
            else:
                stacked.append(We[j])
        vectors = np.stack(stacked)
        #emb[i,:] = w[i,:].dot(vectors) / np.count_nonzero(w[i,:])
        nonzeros = np.sum(m[i,:])
        emb[i, :] = np.divide(w[i, :].dot(vectors), np.sum(m[i,:]), out=np.zeros(dim), where=nonzeros!=0)  # where there is a word
    del x
    del w
    gc.collect()
    return emb

def compute_pc(X,npc=1):
    """
    Compute the principal components. DO NOT MAKE THE DATA ZERO MEAN!
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: component_[i,:] is the i-th pc
    """
    svd = TruncatedSVD(n_components=npc, n_iter=7, random_state=0)
    print('Computing principal components...')
    svd.fit(X)
    return svd.components_

def remove_pc(X, npc=1):
    """
    Remove the projection on the principal components
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: XX[i, :] is the data point after removing its projection
    """
    print('Removing principal component...')
    pc = compute_pc(X, npc)
    if npc == 1:
        XX = X - X.dot(pc.transpose()) * pc
    else:
        XX = X - X.dot(pc.transpose()).dot(pc)
    return XX


def SIF_embedding(We, x, m, w, rmpc, dim):
    """
    Compute the scores between pairs of sentences using weighted average + removing the projection on the first principal component
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in the i-th sentence
    :param w: w[i, :] are the weights for the words in the i-th sentence
    :param params.rmpc: if >0, remove the projections of the sentence embeddings to their first principal component
    :return: emb, emb[i, :] is the embedding for sentence i
    """
    emb = np.nan_to_num(get_weighted_average(We, x, m, w, dim))
    if rmpc > 0:
        emb = remove_pc(emb, rmpc)
    return emb

def generate_embeddings(docs, all_data, model, words2idx, dim, rmpc=1):
    """
    :param docs: list of strings (i.e. docs), based on which to do the tf-idf weighting.
    :param all_data: dataframe column / list of strings (all tweets)
    :param model: pretrained word vectors
    :param vocab: a dictionary, words['str'] is the indices of the word 'str'
    :param dim: dimension of embeddings
    :param rmpc: number of principal components to remove
    :return:
    """
    print(dim)

    print('Getting word weights...')
    word2weight = word_weights(docs)
    # load sentences
    print('Loading sentences...')
    x, m, w = comments2idx(all_data, words2idx, word2weight)  # x is the array of word indices, m is the binary mask indicating whether there is a word in that location
    print('Creating embeddings...')
    return SIF_embedding(model, x, m, w, rmpc, dim)  # embedding[i,:] is the embedding for sentence i

def main():

    stop_words = set(stopwords.words('english'))

    VEC_PATH = '/Users/anthonysicilia/Desktop/GoogleNews-vectors-negative300.bin'
    ABOUT_SHOOTING = set([line.strip() for line in open('about_shooting.txt')])
    vectors = KeyedVectors.load_word2vec_format(datapath(VEC_PATH), binary=True)
    words2idx = dict()
    j = 0
    d = 300

    comments = []
    ids = []

    for comment_path in os.listdir('comments/'):

        with open('comments/' + comment_path) as f:
            
            try:
                x = json.load(f)
            except:
                print('Error Loading File.')
                exit()
            try:
                x = x['comments']
            except:
                print('Expected "comment" field. Field not found.')
                exit()

            for comment in x:
                if comment['link_id'].split('_')[1] not in ABOUT_SHOOTING:
                    continue
                if comment['body'] in ['[deleted]', '[removed]']:
                    continue
                body = []
                text = re.sub(r'https?://\S+', '', comment['body'])
                text = re.sub(r'[,.;@#?!&$]+\ *', '', text, flags=re.VERBOSE)
                for word in word_tokenize(text):
                    if word not in stop_words and word in vectors:
                        if word not in words2idx:
                            words2idx[word] = j; j += 1
                        body.append(word)
                if len(body) > 0:
                    comments.append(' '.join(body))
                    ids.append(comment['id'])
    _vectors = np.zeros((len(words2idx), 300))
    for word,i in words2idx.items():
        _vectors[i] = vectors[word]
    vectors = _vectors
    gc.collect()
    embeddings = generate_embeddings(comments, comments, vectors, words2idx, d)
    
    with open('labels/index.txt', 'w') as f:
        f.write('index,reddit_id\n')
        for i, id_ in enumerate(ids):
            f.write(f'{i},{id_}\n')
    np.savetxt(f'vecs.txt', np.array(embeddings))

if __name__ == '__main__':
    main()