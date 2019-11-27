from gensim.test.utils import datapath
from gensim.models import KeyedVectors
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import json
import os
import re

global STOP_WORDS;
STOP_WORDS = set(stopwords.words('english'))
ABOUT_SHOOTING = set([line.strip() for line in open('about_shooting.txt')])

def valid(word):
    global STOP_WORDS
    return word not in STOP_WORDS

def main():
    global ABOUT_SHOOTING

    VEC_PATH = '/Users/anthonysicilia/Desktop/GoogleNews-vectors-negative300.bin'
    vectors = KeyedVectors.load_word2vec_format(datapath(VEC_PATH), binary=True)

    data = []
    ids = []

    for comment_path in os.listdir('comments/'):

        save_path = comment_path.split('_')[0]

        with open('comments/' + comment_path) as f:
            
            try:
                comments = json.load(f)
            except:
                print('Error Loading File.')
                exit()
            try:
                comments = comments['comments']
            except:
                print('Expected "comment" field. Field not found.')
                exit()

            for comment in comments:
                if comment['link_id'].split('_')[1] not in ABOUT_SHOOTING:
                    continue
                body = []
                for word in word_tokenize(comment['body']):
                    if valid(word) and word in vectors:
                        body.append(vectors[word])
                if len(body) > 1:
                    body = np.array(body)
                    sentence = np.mean(body, axis=0)
                    data.append(sentence)
                    ids.append(comment['id'])

    with open('sentence_index.txt', 'w') as f:
        f.write('index, reddit_id\n')
        for i, id_ in enumerate(ids):
            f.write(f'{i},{id_}\n')
    np.savetxt(f'vecs.txt', np.array(data))

if __name__ == '__main__':
    main()
    

    