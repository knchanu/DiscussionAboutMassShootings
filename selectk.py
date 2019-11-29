from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(style='whitegrid')
import numpy as np

x = np.loadtxt('vecs.txt')

K = [i for i in range(2, 24, 2)]
I = []

for k in K:
    I.append(KMeans(n_clusters=k).fit(x).inertia_)

plt.plot(K, I)
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.savefig('select-k')