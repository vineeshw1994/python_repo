import numpy as np
a = np.array([1, 2, 3])
x = a.view()
x[0] = 10
print(a) # [10  2  3]
print(x) # [10  2  3]