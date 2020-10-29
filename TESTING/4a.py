

N = 10
import numpy as np

probs = [(1-(2**-n))*(2**-( ((n-1)*(n)) /2)) for n in range(1,N)]
print(probs)
vals = [(n+1)*i for n,i in enumerate(probs)]
print(vals)
e = sum(vals)
print(e)

import random
arr = []
for i in range(1000000):
    count = 1

    while True:

        a = random.randint(0,2**(count)-1)
        b = random.randint(0,2**(count)-1)
        #print(a,b)

        if a == b:
            count+=1
        else:
            break
    

    arr.append(count)



mean = float(sum(arr))/len(arr)
print(mean)