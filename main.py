# -*- coding: utf-8 -*-
from matrix import Matrix, Scalar

m1 = Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
])
m2 = Matrix([
    [1, 1, -1],
    [-2, 0, 1],
    [0, 2, 1],
])

# print(m1)
# print()
# print(m2)
# print()
print(m2 * Scalar(2))
print(Scalar(2) * m2)
