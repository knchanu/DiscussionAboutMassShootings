import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from nltk import word_tokenize
import pandas as pd
import json
import os
import re

VEC_PATH = '/Users/anthonysicilia/Desktop/GoogleNews-vectors-negative300.bin'
stopwords = set(stopwords.words('english'))
stopwords = stopwords.union(set([word.strip() for word in open('stopwords.txt')]))
vectors = KeyedVectors.load_word2vec_format(datapath(VEC_PATH), binary=True)
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
                text = re.sub(r'https?://\S+', '', comment['body'])
                text = re.sub(r'[,.;@#?!&$]+\ *', '', text, flags=re.VERBOSE)
                comments[comment['id']] = ' '.join([word for word in word_tokenize(text)
                    if word not in stopwords and word in vectors])

df = pd.read_csv('labels/clusters.txt')
for l in set(df['cluster']):
    idx = df['cluster'] == l
    text = ' '.join([comments[id_] for id_ in df[idx]['reddit_id']])
    wordcloud = WordCloud(background_color='white', stopwords=stopwords,
        max_words=500, min_font_size=7, max_font_size=75, width=600, height=300).generate(text)
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(f'viz/cluster={l}'); plt.clf()