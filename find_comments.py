import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from nltk import word_tokenize
import pandas as pd
import numpy as np
import json
import os
import re

comments = dict()
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
                comments[comment['id']] = comment['body']

df = pd.read_csv('labels/clusters.txt')
with open('comment-examples.txt', 'w') as f:
    for l in set(df['cluster']):
        cdf = df[df['cluster']==l]
        rand = np.random.choice(cdf['reddit_id'], 50)
        f.write(f'Cluster = {l}\n')
        for r in rand:
            if str(r) in comments:
                f.write(f'{comments[str(r)]}\n')
                f.write('-----\n')
            else:
                print(r)
        f.write('=====\n')
        f.write('=====')
        f.write('=====')