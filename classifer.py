from nltk import PorterStemmer as Stemmer
from nltk import word_tokenize
import json
import os

stemmer = Stemmer()

stems = set(['shoot', 'shooter'])

folder = 'submissions/'
about_shooting = set()
for path in os.listdir(folder):
    with open(folder + path) as f:
        data = json.load(f)
        for x in data['comments']:
            for word in word_tokenize(x['title']):
                if stemmer.stem(word) in stems:
                    about_shooting.add(x['id'])
            if 'selftext' in x:
                for word in word_tokenize(x['selftext']):
                    if stemmer.stem(word) in stems:
                        about_shooting.add(x['id'])

folder = 'comments/'
for path in os.listdir(folder):
    with open(folder + path) as f:
        data = json.load(f)
        for x in data['comments']:
            for word in word_tokenize(x['body']):
                if stemmer.stem(word) in stems:
                    about_shooting.add(x['link_id'].split('_')[1])

with open('about_shooting.txt', 'w') as f:
    for link in about_shooting:
        f.write(f'{link}\n')
