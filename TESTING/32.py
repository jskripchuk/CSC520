a=1
b=2
c=4
d=7

n=100000

p=1
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
            r = random.random()
            if r < p:
                total+=6
                break
            else:
                total+=7

    l.append(total)


m = sum(l)/len(l)
print(m)

print("E(X)", (7+6*p+7*(1-p))/(2-(1-p)))