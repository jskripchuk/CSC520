import random
import math


def chan_clear(N,p):
    arr = [0]*N

    for i in range(N):
        r = random.random()

        if r < p:
            arr[i] = 1

    return sum(arr) == 1 


N = 10000
p = 2/N

succ = 0
t=10000
results = []

alpha = N*p*((1-p)**(N-1))
print(alpha)
print(1/(2*math.exp(-2)))

for i in range(t):
    cur = 0
    while True:
        r = random.random()
        cur+=1

        # if it succeds, break
        if r<alpha:
            break
    results.append(cur)

mean = sum(results)/len(results)
print(mean)

            

