c=15-2
a=-5
b=-7

#c=2
#a=5
#b=7

n=100000

l = []

import random

for i in range(n):
    total = 0

    while True:
        st = random.choice(["A","B","C"])

        if st=="A":
            total+=a
        elif st=="B":
            total+=b
        else:
            total+=c
            break

    l.append(total)


m = sum(l)/len(l)
print(m)