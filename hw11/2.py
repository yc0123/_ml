import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from sklearn.cluster import SpectralClustering

X, y = make_circles(n_samples=1000, factor=0.5, noise=0.05, random_state=1)

model = SpectralClustering(n_clusters=2, affinity="nearest_neighbors", random_state=1)
labels = model.fit_predict(X)

plt.scatter(X[:, 0], X[:, 1], c=labels, cmap="Paired")
plt.show()