import numpy as np 
a = np.array([1, 2, 3])
x = a.copy()
x[0] = 10

print(a) # [1 2 3]
print(x) # [10  2  3]