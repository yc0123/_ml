# https://chatgpt.com/share/68007776-9eb8-8010-87f1-d943d96edb38

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs

# 1. 產生資料點 (兩個 cluster 加上一些 noise)
centers = [[2, 2], [-2, -1]]
cluster_std = [0.5, 0.5]
X, _ = make_blobs(n_samples=300, centers=centers, cluster_std=cluster_std, random_state=42)

# 加入一些 noise 點
noise = np.random.uniform(low=-6, high=6, size=(30, 2))
X = np.vstack([X, noise])

# 2. DBSCAN 分群
dbscan = DBSCAN(eps=0.6, min_samples=5)
labels = dbscan.fit_predict(X)

# 3. 畫圖（視覺化分群結果）
plt.figure(figsize=(8, 6))
unique_labels = set(labels)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        # noise 點
        col = [0, 0, 0, 1]  # 黑色
    class_member_mask = (labels == k)
    xy = X[class_member_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

plt.title("DBSCAN clustering with noise")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.show()
