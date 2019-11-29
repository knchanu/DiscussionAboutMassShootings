from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

x = np.loadtxt('vecs.txt')
labels = KMeans(n_clusters=8, random_state=22).fit_predict(x)
df = pd.read_csv('labels/index.txt')
index = {i : id_ for i,id_ in zip(
    df['index'].astype(int), df['reddit_id'].astype(str))}

with open('labels/clusters.txt', 'w') as out:
    out.write('cluster,reddit_id\n')
    for i,l in enumerate(labels):
        out.write(f'{l},{index[i]}\n')

