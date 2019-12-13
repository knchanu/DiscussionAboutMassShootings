from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(style='white')
from datetime import datetime
import numpy as np
import pandas as pd
import json
import os
import re

with open(f'microtime/pval.txt', 'w') as f:
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
        return 'a) 1 day'
    elif (time - ref).days < 7:
        return 'b) 1 week'
    elif (time - ref).days < 14:
        return 'c) 2 weeks'
    else:
        return 'd) 1 month'


aclusters = pd.DataFrame()
xticks = ['polarized', 'neutral', 'opinion', 
    'locations/facts', 'updates', 'law/politics', 'hostile', 'positive']
sns.set(context='poster', style='white')

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
    clusters['city'] = save_path
    clusters = clusters[~clusters['time'].isnull()]
    clusters['count'] = 1.0
    aclusters = pd.concat([aclusters, clusters])
    df = clusters.pivot_table(
        index='time', columns='cluster', 
        values='count', aggfunc=sum)
    chi2, p, dof, expected = chi2_contingency(df.values)
    fig, ax = plt.subplots(figsize=(20, 12))
    # for i in range(df.values.shape[0]):
    #     df.values[i] = df.values[i] / df.values[i].sum()
    sns.heatmap(df, ax=ax, cmap='Blues', xticklabels=xticks)
    plt.xticks(rotation='horizontal')
    plt.title(f'Number of comments (city = {save_path})')
    plt.tight_layout()
    plt.savefig(f'microtime/{save_path}')
    with open(f'microtime/pval.txt', 'a') as f:
        f.write(f'{save_path} p-value: {p}\n')

for c in set(aclusters['city']):
    cidx = aclusters['city'] == c
    aclusters.loc[cidx,'count'] = aclusters[cidx]['count'].astype(float) / aclusters[cidx]['count'].sum()

for l in set(aclusters['cluster']):
    df = aclusters[aclusters['cluster'] == l]
    df = df.groupby(['time', 'city']).sum().reset_index()
    for c in set(df['city']):
        cidx = df['city'] == c
        df.loc[cidx,'count'] = df[cidx]['count'].astype(float) / df[cidx]['count'].sum()
    plt.clf()
    count = 'Percent of Comments'
    df[count] = df['count']
    sns.pointplot(x="time", y=count, hue="city",
        data=df, dodge=True)
    plt.title(f'Percent of comments in each time-window (cluster = {xticks[int(l)]})')
    plt.tight_layout()
    plt.savefig(f'all-cities/cluster={l}')

for t in set(aclusters['time']):
    df = aclusters[aclusters['time'] == t]
    df = df.groupby(['cluster', 'city']).sum().reset_index()
    for c in set(df['city']):
        cidx = df['city'] == c
        df.loc[cidx,'count'] = df[cidx]['count'].astype(float) / df[cidx]['count'].sum()
    plt.clf()
    count = 'Percent of Comments'
    df[count] = df['count']
    df['cluster'] = df['cluster'].apply(lambda l: xticks[l])
    sns.barplot(x="cluster", y=count, hue="city",
        data=df, dodge=True)
    plt.title(f'Percent of comments in each cluster (time = {t})')
    plt.tight_layout()
    plt.savefig(f'all-cities/time={t}')

