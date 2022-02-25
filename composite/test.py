import numpy as np

mat = np.random.rand(10, 10)
idx = np.zeros((10,10))
idx[1,1] = 1
idx[1,2] = 1
idx = idx.astype(np.bool)
mat[idx] = 100
print('hello')