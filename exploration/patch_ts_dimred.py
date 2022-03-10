import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt

infile = 'patch_average_ts.txt'
#
#
# names2 =
df = pd.read_csv(infile, delimiter='\t', header=None)
rows, cols = df.shape
n_timepts = int((cols-2)/4)

names1 = ['lat','lon']
names2 = ['{}_{}'.format(channel, i) for i in range(0, n_timepts) for channel in ['b', 'g', 'r', 'nir']]
names = names1 + names2

df.columns = names
df = df.dropna()
scaler = StandardScaler()
pca = PCA(n_components=2)
X = scaler.fit_transform(df.iloc[:, 2:])
pca.fit(X)

data_red = pca.transform(X)

plt.scatter(data_red[:,0], data_red[:,1], marker='.')
plt.show()


print('hello')