import numpy as np

def softmax(x):
    e = np.exp(x - x.max())
    return e / e.sum()

Q = np.array([[1, 0], [0, 1], [1, 0]], float)
K = np.array([[1, 1], [0, 1], [1, 0]], float)
V = np.array([[1, 0], [0, 1], [0, 1]], float)

scores = Q @ K.T            # 3x3 相似度
W = np.array([softmax(r) for r in scores])
out = W @ V

np.set_printoptions(precision=2, suppress=True)
print("相似度:\n", scores)
print("权重:\n", W)
print("输出:\n", out)