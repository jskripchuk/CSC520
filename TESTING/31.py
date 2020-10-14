a=1
b=3
c=5
d=7

n=100000

l = []

import random

for i in range(n):
    total = 0

    while True:
        st = random.choice(["A","B","C","D"])

        if st=="A":
            total+=a
            break
        elif st=="B":
            total+=b
        elif st=="C":
            total+=c
        else:
            total+=d

    l.append(total)


m = sum(l)/len(l)
print(m)