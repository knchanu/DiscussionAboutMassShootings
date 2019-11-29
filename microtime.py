from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(style='white')
from datetime import datetime
import numpy as np
import pandas as pd
import json
import os
import re

with open(f'microtime/pvals.txt', 'w') as f:
    f.write('chi2test p-values\n')

paths = [
    '/Users/anthonysicilia/Desktop/SCProject/comments/pittsburgh_start=2018-10-27-00:00:00_end=2018-11-27-00:00:00_ep=comment.json',
    '/Users/anthonysicilia/Desktop/SCProject/comments/lasvegas_start=2017-10-01-00:00:00_end=2017-11-01-00:00:00_ep=comment.json',
    '/Users/anthonysicilia/Desktop/SCProject/comments/orlando_start=2016-06-12-00:00:00_end=2016-07-12-00:00:00_ep=comment.json',
    '/Users/anthonysicilia/Desktop/SCProject/comments/elpaso_start=2019-08-03-00:00:00_end=2019-09-03-00:00:00_ep=comment.json'
    ]
refs = [
    # year, month, day[, hour[, minute
    (2018, 10, 27, 9, 54),
    (2017, 10, 1, 12 + 10, 5),
    (2016, 6, 12, 2, 2),
    (2019, 8, 3, 10, 39)
    ]

def time_class(time, ref):
    time = datetime.fromtimestamp(time)
    ref = datetime(*ref)
    if (time - ref).days < 1:
        return 0
    elif (time - ref).days < 7:
        return 1
    elif (time - ref).days < 14:
        return 2
    else:
        return 3

for comment_path, ref in zip(paths, refs):

    time = dict()

    save_path = comment_path.split('comments/')[1].split('_')[0]

    with open(comment_path) as f:
            
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
                time[comment['id']] = time_class(int(comment['created_utc']), ref)

    clusters = pd.read_csv('labels/clusters.txt')
    clusters['time'] = clusters['reddit_id'].apply(lambda id_: 
        time[id_] if id_ in time else None)
    clusters = clusters[~clusters['time'].isnull()]
    clusters['time'] = clusters['time'].astype(int)
    clusters['count'] = 1
    df = clusters.groupby(['time', 'cluster']).count().reset_index()
    n = len(set(clusters['cluster']))
    m = len(set(clusters['time']))
    table = np.zeros((m, n))
    for i,c in enumerate(df['count']):
        table[i // n, i % n] = c
    chi2, p, dof, expected = chi2_contingency(table)
    for i in range(table.shape[0]):
        table[i] = table[i] / table[i].sum()
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.heatmap(table, yticklabels=['1 day', '1 week', '2 weeks', '1 month'], ax=ax,
        cmap='Blues')
    plt.title(f'{save_path}')
    plt.savefig(f'microtime/{save_path}')
    with open(f'microtime/pvals.txt', 'a') as f:
        f.write(f'{save_path} p-value: {p}\n')

